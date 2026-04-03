"""Single source of truth for categories and subcategories.

Reads categories.md at repo root. Every category implicitly has a "General"
subcategory even if not listed in the file.

Format::

    # Personal
    - Food [Coffee, Delivery, Fast Food]
    - Insurance [Auto, Health]
    - Gifts
    - Credit Card Payment [exclude]
    - Income [Athena Health, Patient Payments] [exclude]

    # BFM
    ...

Categories marked with [exclude] are excluded from spending reports.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Optional

log = logging.getLogger(__name__)

# ── Module-level cache ────────────────────────────────────────────────────────
_cache: dict[str, dict[str, list[str]]] = {}
_cache_excludes: dict[str, set[str]] = {}
_cache_mtime: float = 0.0

_SECTION_MAP = {
    "personal": "Personal",
    "company": "BFM",
    "luxelegacy": "LL",
}

# Matches: - CategoryName [sub1, sub2] [exclude]
# Groups: (1) category name, (2) optional first bracket content, (3) optional second bracket
_LINE_RE = re.compile(
    r"^- (.+?)(?:\s*\[([^\]]+)\])?(?:\s*\[([^\]]+)\])?\s*$"
)


def _categories_path() -> str:
    """Return absolute path to categories.md."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "categories.md",
    )


def _parse_file(path: str) -> tuple[dict[str, dict[str, list[str]]], dict[str, set[str]]]:
    """Parse categories.md into categories and exclusion sets.

    Returns:
        (categories, excludes) where:
        - categories: {section: {category: [subcategories]}}
        - excludes: {section: set(excluded category names)}
    """
    categories: dict[str, dict[str, list[str]]] = {}
    excludes: dict[str, set[str]] = {}
    current_section: Optional[str] = None

    with open(path, "r") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# "):
                current_section = line[2:].strip()
                categories[current_section] = {}
                excludes[current_section] = set()
                continue
            if current_section is None:
                continue
            m = _LINE_RE.match(line)
            if m:
                cat = m.group(1).strip()
                bracket1 = m.group(2)
                bracket2 = m.group(3)

                subs = ["General"]
                is_excluded = False

                # Parse bracket groups
                for bracket in (bracket1, bracket2):
                    if bracket is None:
                        continue
                    if bracket.strip().lower() == "exclude":
                        is_excluded = True
                    else:
                        subs += [s.strip() for s in bracket.split(",") if s.strip()]

                categories[current_section][cat] = subs
                if is_excluded:
                    excludes[current_section].add(cat)

    return categories, excludes


def _ensure_cache() -> None:
    """Reload cache if the file has changed."""
    global _cache, _cache_excludes, _cache_mtime

    path = _categories_path()
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return

    if mtime != _cache_mtime:
        _cache, _cache_excludes = _parse_file(path)
        _cache_mtime = mtime


def load_categories(entity_key: str) -> dict[str, list[str]]:
    """Load categories for an entity from categories.md.

    Returns dict mapping category name to list of subcategory names.
    "General" is always included as the first subcategory.
    Results are cached and invalidated when the file changes.
    """
    _ensure_cache()
    section = _SECTION_MAP.get(entity_key)
    if section is None:
        return {}
    return _cache.get(section, {})


def excluded_categories(entity_key: str) -> tuple[str, ...]:
    """Return tuple of category names marked [exclude] for an entity."""
    _ensure_cache()
    section = _SECTION_MAP.get(entity_key)
    if section is None:
        return ()
    return tuple(sorted(_cache_excludes.get(section, set())))


def all_category_names(entity_key: str) -> list[str]:
    """Return sorted list of category names for an entity."""
    return sorted(load_categories(entity_key).keys())


def subcategory_names(entity_key: str, category: str) -> list[str]:
    """Return subcategory names for a category. General always first."""
    cats = load_categories(entity_key)
    return cats.get(category, ["General"])


def validate_references() -> list[str]:
    """Check that hardcoded category references in code match categories.md.

    Returns list of warning strings (empty if all references are valid).
    Called once on app startup.
    """
    _ensure_cache()
    warnings: list[str] = []

    # Check _KEYWORD_RULES in core/categorize.py
    try:
        from core.categorize import _KEYWORD_RULES
        # Build set of all category names across all entities
        all_cats: set[str] = set()
        for section_cats in _cache.values():
            all_cats.update(section_cats.keys())

        for keywords, cat, subcat, conf in _KEYWORD_RULES:
            if cat not in all_cats:
                warnings.append(
                    f"Keyword rule references category '{cat}' which is not in categories.md"
                )
    except ImportError:
        pass

    return warnings
