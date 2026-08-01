#!/usr/bin/env bash
set -Eeuo pipefail
set +x

export AWS_DEFAULT_REGION="us-east-2"
export AWS_PAGER=""

RUN_SUCCESS=0
CLEANUP_FAILED=0
BUCKET_CREATED=0
CLEANUP_AFTER_EPOCH=0
SUFFIX="$(openssl rand -hex 8)"
BUCKET="ledger-s3-proof-${SUFFIX}"
PREFIX="proof/${SUFFIX}/"
DATA_KEY="${PREFIX}synthetic-envelope.bin"
MANIFEST_KEY="${PREFIX}manifest.json"
POLICY_NAME="LedgerS3ProofPolicy"
UPLOADER_ROLE="LedgerS3Proof-Uploader-${SUFFIX}"
OBSERVER_ROLE="LedgerS3Proof-Observer-${SUFFIX}"
RESTORE_ROLE="LedgerS3Proof-Restore-${SUFFIX}"
RETENTION_ROLE="LedgerS3Proof-Retention-${SUFFIX}"
ROLE_NAMES=("$UPLOADER_ROLE" "$OBSERVER_ROLE" "$RESTORE_ROLE" "$RETENTION_ROLE")
TMP_DIR="$(mktemp -d)"
PAYLOAD="${TMP_DIR}/synthetic-envelope.bin"
MANIFEST="${TMP_DIR}/manifest.json"
RESTORED="${TMP_DIR}/restored.bin"
TRUST_POLICY="${TMP_DIR}/trust.json"
UPLOADER_POLICY="${TMP_DIR}/uploader.json"
OBSERVER_POLICY="${TMP_DIR}/observer.json"
RESTORE_POLICY="${TMP_DIR}/restore.json"
RETENTION_POLICY="${TMP_DIR}/retention.json"
DATA_VERSION=""
MANIFEST_VERSION=""
ACCOUNT_ID=""
CALLER_ARN=""
TRUST_PRINCIPAL=""

mark() {
  printf '%s\n' "$1"
}

fail() {
  mark "CHECK=failed:$1"
  exit 1
}

expect_allow() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    mark "ALLOW=passed:${label}"
  else
    fail "allow:${label}"
  fi
}

expect_denied() {
  local label="$1"
  shift
  local error_file="${TMP_DIR}/deny-error"
  : >"$error_file"
  if "$@" >/dev/null 2>"$error_file"; then
    fail "denial-unexpected:${label}"
  fi
  if grep -Eqi 'AccessDenied|not authorized|UnauthorizedOperation' "$error_file"; then
    mark "DENY=passed:${label}"
  else
    fail "denial-ambiguous:${label}"
  fi
}

capture_value() {
  local output_name="$1"
  local label="$2"
  shift 2
  local captured
  if ! captured="$("$@" 2>/dev/null)"; then
    fail "capture:${label}"
  fi
  if [[ -z "$captured" || "$captured" == "None" || "$captured" == "null" ]]; then
    fail "capture-empty:${label}"
  fi
  printf -v "$output_name" '%s' "$captured"
  mark "ALLOW=passed:${label}"
}

assume_role() {
  local prefix="$1"
  local role_name="$2"
  local credentials=""
  local attempt
  for attempt in {1..12}; do
    if credentials="$(aws sts assume-role \
      --role-arn "arn:aws:iam::${ACCOUNT_ID}:role/${role_name}" \
      --role-session-name "ledger-s3-proof" \
      --duration-seconds 900 \
      --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
      --output text 2>/dev/null)"; then
      break
    fi
    sleep 5
  done
  [[ -n "$credentials" ]] || fail "assume-role:${prefix}"
  local access secret token
  IFS=$'\t' read -r access secret token <<<"$credentials"
  [[ -n "$access" && -n "$secret" && -n "$token" ]] || fail "assume-role-fields:${prefix}"
  printf -v "${prefix}_ACCESS" '%s' "$access"
  printf -v "${prefix}_SECRET" '%s' "$secret"
  printf -v "${prefix}_TOKEN" '%s' "$token"
  mark "ROLE_SESSION=passed:${prefix}"
}

delete_bucket_contents() {
  [[ "$BUCKET_CREATED" -eq 1 ]] || return 0

  if [[ "$CLEANUP_AFTER_EPOCH" -gt 0 ]]; then
    local now_epoch remaining
    while true; do
      now_epoch="$(date -u +%s)"
      if (( now_epoch >= CLEANUP_AFTER_EPOCH )); then
        break
      fi
      remaining=$((CLEANUP_AFTER_EPOCH - now_epoch))
      mark "WAIT=retention-expiry:${remaining}s"
      if (( remaining > 30 )); then
        sleep 30
      else
        sleep "$remaining"
      fi
    done
  fi

  local versions_file="${TMP_DIR}/versions.tsv"
  local markers_file="${TMP_DIR}/markers.tsv"
  if ! aws s3api list-object-versions \
    --bucket "$BUCKET" \
    --prefix "$PREFIX" \
    --query 'Versions[].[Key,VersionId]' \
    --output text >"$versions_file" 2>/dev/null; then
    CLEANUP_FAILED=1
    return
  fi
  while IFS=$'\t' read -r key version_id; do
    [[ -n "$key" && -n "$version_id" ]] || continue
    if ! aws s3api delete-object \
      --bucket "$BUCKET" \
      --key "$key" \
      --version-id "$version_id" >/dev/null 2>&1; then
      CLEANUP_FAILED=1
    fi
  done <"$versions_file"

  if ! aws s3api list-object-versions \
    --bucket "$BUCKET" \
    --prefix "$PREFIX" \
    --query 'DeleteMarkers[].[Key,VersionId]' \
    --output text >"$markers_file" 2>/dev/null; then
    CLEANUP_FAILED=1
    return
  fi
  while IFS=$'\t' read -r key version_id; do
    [[ -n "$key" && -n "$version_id" ]] || continue
    if ! aws s3api delete-object \
      --bucket "$BUCKET" \
      --key "$key" \
      --version-id "$version_id" >/dev/null 2>&1; then
      CLEANUP_FAILED=1
    fi
  done <"$markers_file"
}

cleanup() {
  local original_status=$?
  trap - EXIT
  set +e

  local role_name
  for role_name in "${ROLE_NAMES[@]}"; do
    aws iam delete-role-policy \
      --role-name "$role_name" \
      --policy-name "$POLICY_NAME" >/dev/null 2>&1
    aws iam delete-role --role-name "$role_name" >/dev/null 2>&1
  done

  delete_bucket_contents

  if [[ "$BUCKET_CREATED" -eq 1 ]]; then
    if ! aws s3api delete-bucket --bucket "$BUCKET" >/dev/null 2>&1; then
      CLEANUP_FAILED=1
    fi
  fi

  if [[ "$BUCKET_CREATED" -eq 1 ]] && aws s3api head-bucket --bucket "$BUCKET" >/dev/null 2>&1; then
    CLEANUP_FAILED=1
  fi
  for role_name in "${ROLE_NAMES[@]}"; do
    if aws iam get-role --role-name "$role_name" >/dev/null 2>&1; then
      CLEANUP_FAILED=1
    fi
  done

  rm -rf "$TMP_DIR"

  if [[ "$CLEANUP_FAILED" -eq 0 ]]; then
    mark "CLEANUP=passed:bucket-objects-policies-roles"
  else
    mark "CLEANUP=failed"
    original_status=1
  fi

  if [[ "$original_status" -eq 0 && "$RUN_SUCCESS" -eq 1 ]]; then
    mark "RESULT=success"
  else
    mark "RESULT=failed"
    original_status=1
  fi
  exit "$original_status"
}

trap cleanup EXIT

mark "RUN=started"

capture_value ACCOUNT_ID "caller-session" \
  aws sts get-caller-identity --query Account --output text

capture_value CALLER_ARN "caller-principal-shape" \
  aws sts get-caller-identity --query Arn --output text

if [[ "${AWS_ROLE_ARN:-}" =~ ^arn:aws:iam::${ACCOUNT_ID}:role/.+[^/]$ ]]; then
  TRUST_PRINCIPAL="$AWS_ROLE_ARN"
  mark "PRINCIPAL_PREFLIGHT=passed:session-role-arn"
elif [[ "$CALLER_ARN" =~ ^arn:aws:iam::${ACCOUNT_ID}:role/.+[^/]$ ]]; then
  TRUST_PRINCIPAL="$CALLER_ARN"
  mark "PRINCIPAL_PREFLIGHT=passed:caller-role-arn"
else
  mark "PRINCIPAL_PREFLIGHT=stopped:stable-role-not-derivable"
  fail "stable-principal-ambiguous"
fi

printf 'ledger-synthetic-envelope-v1\n' >"$PAYLOAD"
openssl rand -base64 96 >>"$PAYLOAD"
printf '{"schema":"ledger.synthetic.recovery.v1","entity":"synthetic","files":["synthetic-envelope.bin"]}\n' >"$MANIFEST"
SOURCE_HASH="$(sha256sum "$PAYLOAD" | awk '{print $1}')"

cat >"$TRUST_POLICY" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "${TRUST_PRINCIPAL}"},
    "Action": "sts:AssumeRole"
  }]
}
JSON

cat >"$UPLOADER_POLICY" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::${BUCKET}/${PREFIX}*"
  }]
}
JSON

cat >"$OBSERVER_POLICY" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:ListBucketVersions"],
      "Resource": "arn:aws:s3:::${BUCKET}",
      "Condition": {"StringLike": {"s3:prefix": ["${PREFIX}", "${PREFIX}*"]}}
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObjectRetention", "s3:GetObjectLegalHold"],
      "Resource": "arn:aws:s3:::${BUCKET}/${PREFIX}*"
    }
  ]
}
JSON

cat >"$RESTORE_POLICY" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:ListBucketVersions"],
      "Resource": "arn:aws:s3:::${BUCKET}",
      "Condition": {"StringLike": {"s3:prefix": ["${PREFIX}", "${PREFIX}*"]}}
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObjectVersion", "s3:GetObjectRetention", "s3:GetObjectLegalHold"],
      "Resource": "arn:aws:s3:::${BUCKET}/${PREFIX}*"
    }
  ]
}
JSON

cat >"$RETENTION_POLICY" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucketVersions",
      "Resource": "arn:aws:s3:::${BUCKET}",
      "Condition": {"StringLike": {"s3:prefix": ["${PREFIX}", "${PREFIX}*"]}}
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObjectRetention", "s3:PutObjectRetention"],
      "Resource": "arn:aws:s3:::${BUCKET}/${PREFIX}*"
    }
  ]
}
JSON

expect_allow "bucket-create" aws s3api create-bucket \
  --bucket "$BUCKET" \
  --create-bucket-configuration LocationConstraint=us-east-2 \
  --object-lock-enabled-for-bucket
BUCKET_CREATED=1

expect_allow "public-access-block" aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

capture_value VERSIONING_STATUS "bucket-versioning" \
  aws s3api get-bucket-versioning --bucket "$BUCKET" --query Status --output text
[[ "$VERSIONING_STATUS" == "Enabled" ]] || fail "versioning-not-enabled"

capture_value OBJECT_LOCK_STATUS "bucket-object-lock" \
  aws s3api get-object-lock-configuration \
  --bucket "$BUCKET" \
  --query 'ObjectLockConfiguration.ObjectLockEnabled' \
  --output text
[[ "$OBJECT_LOCK_STATUS" == "Enabled" ]] || fail "object-lock-not-enabled"

expect_allow "uploader-role-create" aws iam create-role \
  --role-name "$UPLOADER_ROLE" \
  --assume-role-policy-document "file://${TRUST_POLICY}" \
  --max-session-duration 3600
expect_allow "uploader-policy-attach" aws iam put-role-policy \
  --role-name "$UPLOADER_ROLE" \
  --policy-name "$POLICY_NAME" \
  --policy-document "file://${UPLOADER_POLICY}"

expect_allow "observer-role-create" aws iam create-role \
  --role-name "$OBSERVER_ROLE" \
  --assume-role-policy-document "file://${TRUST_POLICY}" \
  --max-session-duration 3600
expect_allow "observer-policy-attach" aws iam put-role-policy \
  --role-name "$OBSERVER_ROLE" \
  --policy-name "$POLICY_NAME" \
  --policy-document "file://${OBSERVER_POLICY}"

expect_allow "restore-role-create" aws iam create-role \
  --role-name "$RESTORE_ROLE" \
  --assume-role-policy-document "file://${TRUST_POLICY}" \
  --max-session-duration 3600
expect_allow "restore-policy-attach" aws iam put-role-policy \
  --role-name "$RESTORE_ROLE" \
  --policy-name "$POLICY_NAME" \
  --policy-document "file://${RESTORE_POLICY}"

expect_allow "retention-role-create" aws iam create-role \
  --role-name "$RETENTION_ROLE" \
  --assume-role-policy-document "file://${TRUST_POLICY}" \
  --max-session-duration 3600
expect_allow "retention-policy-attach" aws iam put-role-policy \
  --role-name "$RETENTION_ROLE" \
  --policy-name "$POLICY_NAME" \
  --policy-document "file://${RETENTION_POLICY}"

assume_role U "$UPLOADER_ROLE"
assume_role O "$OBSERVER_ROLE"
assume_role R "$RESTORE_ROLE"
assume_role T "$RETENTION_ROLE"

capture_value DATA_VERSION "uploader-data-upload" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api put-object \
  --bucket "$BUCKET" \
  --key "$DATA_KEY" \
  --body "$PAYLOAD" \
  --server-side-encryption AES256 \
  --query VersionId \
  --output text

capture_value MANIFEST_VERSION "uploader-manifest-upload" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api put-object \
  --bucket "$BUCKET" \
  --key "$MANIFEST_KEY" \
  --body "$MANIFEST" \
  --server-side-encryption AES256 \
  --query VersionId \
  --output text

expect_denied "uploader-list" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api list-object-versions --bucket "$BUCKET" --prefix "$PREFIX"
expect_denied "uploader-read" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api get-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" "${TMP_DIR}/uploader-read"
expect_denied "uploader-delete" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api delete-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"
expect_denied "uploader-retention" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api put-object-retention \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --retention Mode=GOVERNANCE,RetainUntilDate="$(date -u -d '+10 minutes' +%Y-%m-%dT%H:%M:%SZ)"
expect_denied "uploader-legal-hold" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api put-object-legal-hold \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --legal-hold Status=ON
expect_denied "uploader-object-lock-config" \
  env AWS_ACCESS_KEY_ID="$U_ACCESS" AWS_SECRET_ACCESS_KEY="$U_SECRET" AWS_SESSION_TOKEN="$U_TOKEN" \
  aws s3api get-object-lock-configuration --bucket "$BUCKET"

RETENTION_BASE_EPOCH="$(date -u +%s)"
INITIAL_EPOCH=$((RETENTION_BASE_EPOCH + 90))
EXTENDED_EPOCH=$((RETENTION_BASE_EPOCH + 150))
SHORTENED_EPOCH=$((RETENTION_BASE_EPOCH + 120))
INITIAL_ISO="$(date -u -d "@${INITIAL_EPOCH}" +%Y-%m-%dT%H:%M:%SZ)"
EXTENDED_ISO="$(date -u -d "@${EXTENDED_EPOCH}" +%Y-%m-%dT%H:%M:%SZ)"
SHORTENED_ISO="$(date -u -d "@${SHORTENED_EPOCH}" +%Y-%m-%dT%H:%M:%SZ)"

expect_allow "retention-initial" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api put-object-retention \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --retention Mode=GOVERNANCE,RetainUntilDate="$INITIAL_ISO"
CLEANUP_AFTER_EPOCH=$((INITIAL_EPOCH + 10))
expect_allow "retention-read" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api get-object-retention --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"
expect_allow "retention-extend" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api put-object-retention \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --retention Mode=GOVERNANCE,RetainUntilDate="$EXTENDED_ISO"
CLEANUP_AFTER_EPOCH=$((EXTENDED_EPOCH + 10))
expect_denied "retention-shorten-without-bypass" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api put-object-retention \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --retention Mode=GOVERNANCE,RetainUntilDate="$SHORTENED_ISO"
expect_denied "retention-payload-read" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api get-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" "${TMP_DIR}/retention-read"
expect_denied "retention-upload" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api put-object --bucket "$BUCKET" --key "${PREFIX}retention-write" --body "$MANIFEST"
expect_denied "retention-delete" \
  env AWS_ACCESS_KEY_ID="$T_ACCESS" AWS_SECRET_ACCESS_KEY="$T_SECRET" AWS_SESSION_TOKEN="$T_TOKEN" \
  aws s3api delete-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"

capture_value OBSERVED_VERSION_COUNT "observer-list-versions" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api list-object-versions \
  --bucket "$BUCKET" \
  --prefix "$PREFIX" \
  --query 'length(Versions)' \
  --output text
[[ "$OBSERVED_VERSION_COUNT" == "2" ]] || fail "observer-version-count"
expect_allow "observer-retention-metadata" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api get-object-retention --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"
expect_allow "observer-legal-hold-metadata" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api get-object-legal-hold --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"
expect_denied "observer-payload-read" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api get-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" "${TMP_DIR}/observer-read"
expect_denied "observer-upload" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api put-object --bucket "$BUCKET" --key "${PREFIX}observer-write" --body "$MANIFEST"
expect_denied "observer-delete" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api delete-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"
expect_denied "observer-retention-mutation" \
  env AWS_ACCESS_KEY_ID="$O_ACCESS" AWS_SECRET_ACCESS_KEY="$O_SECRET" AWS_SESSION_TOKEN="$O_TOKEN" \
  aws s3api put-object-retention \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --retention Mode=GOVERNANCE,RetainUntilDate="$EXTENDED_ISO"

expect_allow "restore-list-versions" \
  env AWS_ACCESS_KEY_ID="$R_ACCESS" AWS_SECRET_ACCESS_KEY="$R_SECRET" AWS_SESSION_TOKEN="$R_TOKEN" \
  aws s3api list-object-versions --bucket "$BUCKET" --prefix "$PREFIX"
expect_allow "restore-exact-version" \
  env AWS_ACCESS_KEY_ID="$R_ACCESS" AWS_SECRET_ACCESS_KEY="$R_SECRET" AWS_SESSION_TOKEN="$R_TOKEN" \
  aws s3api get-object \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" "$RESTORED"
RESTORED_HASH="$(sha256sum "$RESTORED" | awk '{print $1}')"
[[ "$RESTORED_HASH" == "$SOURCE_HASH" ]] || fail "restore-hash-parity"
mark "RESTORE_HASH=passed"
expect_denied "restore-upload" \
  env AWS_ACCESS_KEY_ID="$R_ACCESS" AWS_SECRET_ACCESS_KEY="$R_SECRET" AWS_SESSION_TOKEN="$R_TOKEN" \
  aws s3api put-object --bucket "$BUCKET" --key "${PREFIX}restore-write" --body "$MANIFEST"
expect_denied "restore-delete" \
  env AWS_ACCESS_KEY_ID="$R_ACCESS" AWS_SECRET_ACCESS_KEY="$R_SECRET" AWS_SESSION_TOKEN="$R_TOKEN" \
  aws s3api delete-object --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION"
expect_denied "restore-retention-mutation" \
  env AWS_ACCESS_KEY_ID="$R_ACCESS" AWS_SECRET_ACCESS_KEY="$R_SECRET" AWS_SESSION_TOKEN="$R_TOKEN" \
  aws s3api put-object-retention \
  --bucket "$BUCKET" --key "$DATA_KEY" --version-id "$DATA_VERSION" \
  --retention Mode=GOVERNANCE,RetainUntilDate="$EXTENDED_ISO"

mark "CAPABILITY_MATRIX=passed"
RUN_SUCCESS=1
