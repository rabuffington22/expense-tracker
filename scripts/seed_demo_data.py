"""Seed demo data for testing. Run on Fly.io via: fly ssh console -C 'python3 /app/scripts/seed_demo_data.py'"""

import os
import sys
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.environ.get("DATA_DIR", "./local_state")
os.makedirs(DATA_DIR, exist_ok=True)

from core.db import init_db, get_db_path

# ── Personal seed data ──────────────────────────────────────────────────────

PERSONAL_MERCHANTS = {
    "Groceries": [
        ("HEB GROCERY", 45, 120),
        ("WHOLE FOODS", 60, 150),
        ("COSTCO", 100, 300),
        ("TARGET", 25, 80),
        ("TRADER JOES", 30, 90),
    ],
    "Dining": [
        ("CHICK-FIL-A", 8, 18),
        ("CHIPOTLE", 10, 22),
        ("STARBUCKS", 4, 9),
        ("DOMINOS PIZZA", 12, 30),
        ("WHATABURGER", 8, 15),
        ("OLIVE GARDEN", 30, 70),
    ],
    "Gas & Auto": [
        ("SHELL OIL", 35, 65),
        ("EXXONMOBIL", 30, 60),
        ("BUCCEES", 40, 70),
        ("DISCOUNT TIRE", 100, 400),
        ("AUTOZONE", 15, 60),
    ],
    "Utilities": [
        ("ONCOR ELECTRIC", 120, 250),
        ("ATMOS ENERGY", 40, 90),
        ("CITY OF DALLAS WATER", 50, 100),
        ("AT&T INTERNET", 65, 65),
    ],
    "Subscriptions": [
        ("NETFLIX", 15, 23),
        ("SPOTIFY", 11, 11),
        ("APPLE ICLOUD", 3, 3),
        ("YOUTUBE PREMIUM", 14, 14),
        ("AMAZON PRIME", 15, 15),
        ("CHATGPT PLUS", 20, 20),
    ],
    "Health & Beauty": [
        ("CVS PHARMACY", 10, 50),
        ("WALGREENS", 8, 35),
        ("GREAT CLIPS", 18, 25),
    ],
    "Kids": [
        ("KUMON", 150, 150),
        ("CHUCKE CHEESE", 25, 60),
        ("FIVE BELOW", 10, 30),
        ("NIKE STORE", 40, 120),
    ],
    "Household": [
        ("HOME DEPOT", 20, 150),
        ("LOWES", 25, 200),
        ("AMAZON", 10, 100),
    ],
    "Pet Supplies": [
        ("PETSMART", 20, 80),
        ("CHEWY", 30, 70),
    ],
    "Clothing": [
        ("OLD NAVY", 25, 80),
        ("NORDSTROM", 40, 150),
        ("TJ MAXX", 20, 70),
    ],
    "Insurance": [
        ("STATE FARM", 180, 180),
        ("GEICO AUTO", 130, 130),
    ],
    "Entertainment": [
        ("AMC THEATRES", 15, 30),
        ("TICKETMASTER", 40, 120),
        ("BARNES & NOBLE", 10, 35),
    ],
    "Travel": [
        ("MARRIOTT", 150, 350),
        ("SOUTHWEST AIRLINES", 200, 450),
        ("ENTERPRISE RENT", 50, 120),
    ],
    "Home Improvement": [
        ("MENARDS", 20, 100),
        ("ACE HARDWARE", 10, 50),
    ],
    "Gifts & Donations": [
        ("HALLMARK", 5, 20),
        ("CHURCHES ONLINE", 100, 100),
        ("GOODWILL", 15, 40),
    ],
    "Electronics": [
        ("BEST BUY", 30, 200),
        ("MICRO CENTER", 20, 150),
    ],
    "Fitness & Wellness": [
        ("LIFETIME FITNESS", 80, 80),
        ("PELOTON", 44, 44),
    ],
    "Education": [
        ("UDEMY", 12, 15),
        ("COURSERA", 50, 50),
    ],
    "Housing": [
        ("CORNERSTONE MORTGAGE", 2200, 2200),
        ("HOA MANAGEMENT", 175, 175),
    ],
    "Student Loans": [
        ("NELNET STUDENT LOAN", 350, 350),
        ("NAVIENT", 280, 280),
    ],
    "Medical": [
        ("BAYLOR SCOTT WHITE", 50, 300),
        ("CVS MINUTE CLINIC", 25, 75),
        ("DR SMITH DDS", 150, 400),
        ("VISION CENTER", 100, 250),
    ],
    "Personal Care": [
        ("SUPERCUTS", 20, 35),
        ("MASSAGE ENVY", 70, 100),
        ("ULTA BEAUTY", 15, 60),
    ],
    "Taxes": [
        ("DENTON COUNTY TAX", 400, 400),
        ("TURBOTAX", 80, 150),
    ],
    "Ranch": [
        ("TRACTOR SUPPLY CO", 30, 200),
        ("ATWOODS", 15, 120),
        ("COTTON ELECTRIC", 80, 150),
        ("RURAL KING", 20, 90),
    ],
    "Charity": [
        ("GATEWAY CHURCH", 200, 200),
        ("ST JUDE DONATION", 50, 50),
        ("RED CROSS", 25, 100),
    ],
    "Auto & Transport": [
        ("JIFFY LUBE", 40, 80),
        ("TEXPRESS TOLLS", 15, 30),
        ("PARK PLACE MOTORS", 100, 500),
        ("UBER", 10, 35),
    ],
}

PERSONAL_INCOME = [
    ("DIRECT DEPOSIT - ACME INC", 4500, 4500),
    ("VENMO CASHOUT", 50, 200),
    ("ZELLE FROM MOM", 100, 300),
]

# Account assignment: map merchant categories to account names
PERSONAL_ACCOUNT_MAP = {
    "Groceries": "Primary Checking",
    "Dining": "Visa Rewards",
    "Gas & Auto": "Visa Rewards",
    "Utilities": "Primary Checking",
    "Subscriptions": "Visa Rewards",
    "Health & Beauty": "Amex",
    "Kids": "Primary Checking",
    "Household": "Amex",
    "Pet Supplies": "Store Card",
    "Clothing": "Store Card",
    "Insurance": "Primary Checking",
    "Entertainment": "Visa Rewards",
    "Travel": "Amex",
    "Home Improvement": "Primary Checking",
    "Gifts & Donations": "Primary Checking",
    "Electronics": "Amex",
    "Fitness & Wellness": "Primary Checking",
    "Education": "Visa Rewards",
    "Housing": "Primary Checking",
    "Student Loans": "Primary Checking",
    "Medical": "Visa Rewards",
    "Personal Care": "Visa Rewards",
    "Taxes": "Primary Checking",
    "Ranch": "Primary Checking",
    "Charity": "Primary Checking",
    "Auto & Transport": "Visa Rewards",
}

PERSONAL_ACCOUNTS = [
    # (name, type, balance_cents, credit_limit_cents, due_day, payment_cents, sort)
    ("Primary Checking", "bank", 420000, 0, None, 0, 0),
    ("Savings", "bank", 1250000, 0, None, 0, 1),
    ("Visa Rewards", "credit_card", 185000, 800000, 22, 18500, 10),
    ("Amex", "credit_card", 62000, 500000, 15, 6200, 11),
    ("Store Card", "credit_card", 34000, 200000, 8, 3400, 12),
]

PERSONAL_RECURRING = [
    # (account_name, merchant, amount_cents, day_of_month)
    ("Primary Checking", "Mortgage Payment", 185000, 15),
    ("Primary Checking", "Car Payment", 42500, 3),
]

# ── Business seed data ──────────────────────────────────────────────────────

BUSINESS_MERCHANTS = {
    "Office Supplies": [
        ("STAPLES", 25, 120),
        ("OFFICE DEPOT", 30, 150),
        ("AMAZON BUSINESS", 15, 200),
    ],
    "Software": [
        ("ADOBE CREATIVE CLOUD", 55, 55),
        ("ZOOM VIDEO", 15, 15),
        ("SLACK TECHNOLOGIES", 13, 13),
        ("QUICKBOOKS ONLINE", 80, 80),
        ("GITHUB", 21, 21),
        ("GOOGLE WORKSPACE", 14, 14),
    ],
    "Travel": [
        ("DELTA AIR LINES", 250, 650),
        ("UNITED AIRLINES", 200, 550),
        ("HILTON HOTELS", 150, 350),
        ("MARRIOTT", 180, 400),
        ("UBER", 15, 45),
        ("LYFT", 12, 40),
    ],
    "Professional Services": [
        ("SMITH & ASSOCIATES CPA", 500, 500),
        ("BAKER LAW GROUP", 750, 750),
        ("CREATIVE MARKETING CO", 1500, 1500),
    ],
    "Marketing": [
        ("GOOGLE ADS", 200, 800),
        ("META ADS", 150, 600),
        ("LINKEDIN ADS", 100, 400),
        ("MAILCHIMP", 50, 50),
    ],
    "Insurance": [
        ("HARTFORD BUSINESS INS", 350, 350),
        ("HISCOX PROFESSIONAL", 180, 180),
    ],
    "Utilities": [
        ("COMCAST BUSINESS", 120, 120),
        ("AT&T BUSINESS", 85, 85),
        ("DALLAS ELECTRIC", 200, 350),
    ],
    "Meals & Entertainment": [
        ("STARBUCKS", 5, 12),
        ("PANERA BREAD", 10, 18),
        ("RUTH'S CHRIS", 80, 200),
        ("CAPITAL GRILLE", 100, 250),
    ],
    "Equipment": [
        ("DELL TECHNOLOGIES", 800, 2500),
        ("APPLE STORE", 500, 1500),
        ("BEST BUY BUSINESS", 200, 800),
    ],
    "Payroll": [
        ("ADP PAYROLL", 8500, 8500),
        ("GUSTO PAYROLL", 3200, 3200),
    ],
    "Rent & Facilities": [
        ("REGUS OFFICE", 1200, 1200),
        ("WEWORK", 800, 800),
    ],
    "Training & Development": [
        ("OREILLY MEDIA", 50, 50),
        ("LINKEDIN LEARNING", 30, 30),
        ("AWS TRAINING", 300, 500),
    ],
    "Shipping & Logistics": [
        ("USPS", 8, 25),
        ("FEDEX", 15, 60),
        ("UPS STORE", 10, 45),
    ],
    "Taxes & Licenses": [
        ("TX COMPTROLLER", 500, 2000),
        ("IRS EFTPS", 2000, 5000),
    ],
    "Legal": [
        ("BAKER MCKENZIE LLP", 500, 2000),
        ("LEGALZOOM", 30, 150),
    ],
    "Consulting": [
        ("MCKINSEY & CO", 2000, 5000),
        ("DELOITTE CONSULTING", 1500, 4000),
    ],
    "Employee Benefits": [
        ("UNITED HEALTHCARE", 1200, 1200),
        ("FIDELITY 401K", 800, 800),
        ("METLIFE DENTAL", 350, 350),
        ("VSP VISION", 120, 120),
    ],
    "Banking & Fees": [
        ("CHASE WIRE FEE", 25, 35),
        ("BANK SERVICE CHARGE", 15, 30),
        ("MERCHANT PROCESSING FEE", 50, 200),
    ],
    "Client Gifts": [
        ("HARRY & DAVID", 40, 120),
        ("TIFFANY & CO", 80, 250),
        ("EDIBLE ARRANGEMENTS", 50, 90),
    ],
    "Vehicle & Fleet": [
        ("ENTERPRISE FLEET", 400, 400),
        ("SHELL FLEET CARD", 150, 300),
        ("FIRESTONE AUTO", 80, 250),
    ],
    "Cleaning & Maintenance": [
        ("JANI-KING", 350, 350),
        ("SERVPRO", 200, 500),
    ],
    "Subscriptions": [
        ("WALL STREET JOURNAL", 40, 40),
        ("BLOOMBERG TERMINAL", 250, 250),
        ("SALESFORCE CRM", 150, 150),
    ],
}

BUSINESS_INCOME = [
    ("CLIENT PAYMENT - WIRE", 8000, 15000),
    ("ACH DEPOSIT - INVOICE", 3000, 8000),
    ("STRIPE TRANSFER", 500, 3000),
]

BUSINESS_ACCOUNT_MAP = {
    "Office Supplies": "Business Checking",
    "Software": "Business Amex",
    "Travel": "Business Amex",
    "Professional Services": "Business Checking",
    "Marketing": "Business Amex",
    "Insurance": "Business Checking",
    "Utilities": "Business Checking",
    "Meals & Entertainment": "Business Amex",
    "Equipment": "Business Amex",
    "Payroll": "Business Checking",
    "Rent & Facilities": "Business Checking",
    "Training & Development": "Business Amex",
    "Shipping & Logistics": "Business Checking",
    "Taxes & Licenses": "Business Checking",
    "Legal": "Business Checking",
    "Consulting": "Business Checking",
    "Employee Benefits": "Business Checking",
    "Banking & Fees": "Business Checking",
    "Client Gifts": "Business Amex",
    "Vehicle & Fleet": "Business Checking",
    "Cleaning & Maintenance": "Business Checking",
    "Subscriptions": "Business Amex",
}

BUSINESS_ACCOUNTS = [
    ("Business Checking", "bank", 1870000, 0, None, 0, 0),
    ("Business Savings", "bank", 4500000, 0, None, 0, 1),
    ("Payroll Account", "bank", 850000, 0, None, 0, 2),
    ("Business Amex", "credit_card", 210000, 1500000, 20, 21000, 10),
]

BUSINESS_RECURRING = [
    ("Business Checking", "Office Rent", 250000, 1),
    ("Business Checking", "Payroll - ADP", 1200000, 15),
]

PERSONAL_LARGE_TXNS = [
    ("BEST BUY", -899.99),
    ("APPLE STORE", -1299.00),
    ("DALLAS VETERINARY", -450.00),
    ("POTTERY BARN", -680.00),
    ("DELTA AIR LINES", -520.00),
]

BUSINESS_LARGE_TXNS = [
    ("CONFERENCE REGISTRATION", -2500.00),
    ("SERVER HARDWARE", -3200.00),
    ("ANNUAL SOFTWARE LICENSE", -1800.00),
]

# ── Extra categories + subcategories for demo richness ───────────────────────

PERSONAL_EXTRA_CATEGORIES = {
    # category: [subcategories]
    "Groceries": ["Produce", "Meat & Seafood", "Dairy", "Bakery", "Frozen", "Snacks", "Beverages", "Organic", "Bulk Items"],
    "Dining": ["Fast Food", "Casual Dining", "Fine Dining", "Coffee & Tea", "Delivery", "Bars & Pubs", "Food Trucks", "Brunch"],
    "Gas & Auto": ["Gas", "Oil Change", "Tires", "Car Wash", "Repairs", "Parking", "Tolls", "Registration"],
    "Utilities": ["Electric", "Gas", "Water", "Internet", "Phone", "Trash & Recycling"],
    "Subscriptions": ["Streaming Video", "Streaming Music", "Cloud Storage", "News & Magazines", "Software", "Gaming", "Fitness Apps"],
    "Health & Beauty": ["Pharmacy", "Vitamins", "Skincare", "Haircare", "Dental", "Vision", "Therapy", "Gym & Fitness"],
    "Kids": ["School Supplies", "Tutoring", "Activities", "Toys", "Clothing", "Diapers & Wipes", "Childcare", "Sports & Camps"],
    "Household": ["Cleaning Supplies", "Furniture", "Decor", "Kitchen", "Storage", "Laundry", "Garden & Outdoor", "Smart Home"],
    "Pet Supplies": ["Food", "Toys", "Vet Visits", "Grooming", "Medications", "Boarding"],
    "Clothing": ["Women", "Men", "Kids", "Shoes", "Accessories", "Activewear", "Outerwear"],
    "Insurance": ["Auto", "Home", "Life", "Umbrella", "Renters"],
    "Entertainment": ["Movies", "Concerts", "Sports Events", "Theme Parks", "Books", "Games", "Hobbies"],
    "Travel": ["Flights", "Hotels", "Car Rental", "Luggage", "Excursions", "Travel Insurance"],
    "Home Improvement": ["Tools", "Hardware", "Paint", "Flooring", "Plumbing", "Electrical", "Landscaping"],
    "Education": ["Tuition", "Books & Supplies", "Online Courses", "Certifications"],
    "Gifts & Donations": ["Birthday", "Holiday", "Wedding", "Charity", "Religious"],
    "Electronics": ["Computers", "Phones", "Tablets", "Accessories", "Smart Home", "Audio"],
    "Fitness & Wellness": ["Gym Membership", "Classes", "Equipment", "Supplements", "Massage & Spa"],
    "Housing": ["Mortgage", "Rent", "HOA Fees", "Property Tax", "Home Warranty"],
    "Student Loans": ["Federal", "Private", "Refinanced"],
    "Medical": ["Primary Care", "Dental", "Vision", "Urgent Care", "Specialist", "Prescriptions"],
    "Personal Care": ["Haircut", "Spa & Massage", "Skincare", "Nails"],
    "Taxes": ["Property Tax", "Income Tax", "Tax Prep"],
    "Ranch": ["Feed & Supplies", "Equipment", "Fencing", "Utilities", "Vet"],
    "Charity": ["Church", "Nonprofit", "Disaster Relief"],
    "Auto & Transport": ["Oil Change", "Tolls", "Repairs", "Rideshare", "Parking"],
}

BUSINESS_EXTRA_CATEGORIES = {
    "Office Supplies": ["Paper & Printing", "Writing Supplies", "Desk Accessories", "Filing & Storage", "Breakroom Supplies"],
    "Software": ["Accounting", "CRM", "Project Management", "Design", "Communication", "Security", "Hosting"],
    "Travel": ["Flights", "Hotels", "Ground Transport", "Per Diem", "Conference Travel", "Client Visits"],
    "Professional Services": ["Legal", "Accounting & Tax", "Consulting", "Recruiting", "IT Support"],
    "Marketing": ["Digital Ads", "Social Media", "Email Marketing", "Print & Direct Mail", "Events & Sponsorships", "Content Creation", "SEO & Analytics"],
    "Insurance": ["General Liability", "Professional Liability", "Workers Comp", "Property", "Cyber Insurance"],
    "Utilities": ["Internet", "Phone", "Electric", "Water", "Security System"],
    "Meals & Entertainment": ["Client Meals", "Team Lunches", "Coffee Runs", "Holiday Events", "Happy Hours"],
    "Equipment": ["Computers", "Monitors & Displays", "Networking", "Furniture", "Printers", "Audio/Video"],
    "Payroll": ["Salaries", "Contractor Payments", "Bonuses", "Payroll Taxes", "Benefits"],
    "Rent & Facilities": ["Office Rent", "Coworking", "Storage", "Maintenance", "Janitorial"],
    "Training & Development": ["Conferences", "Online Courses", "Certifications", "Books & Resources", "Team Workshops"],
    "Shipping & Logistics": ["USPS", "FedEx", "UPS", "Freight", "Packaging Materials"],
    "Taxes & Licenses": ["Federal Tax", "State Tax", "Business License", "Permits", "Franchise Tax"],
    "Legal": ["Contracts", "Compliance", "Litigation", "Intellectual Property"],
    "Consulting": ["Strategy", "IT Consulting", "Management", "Financial Advisory"],
    "Employee Benefits": ["Health Insurance", "401k Match", "Dental", "Vision", "Life Insurance"],
    "Banking & Fees": ["Wire Fees", "Service Charges", "Merchant Processing", "ACH Fees"],
    "Client Gifts": ["Holiday Gifts", "Thank You Gifts", "Event Gifts"],
    "Vehicle & Fleet": ["Lease Payments", "Fuel", "Maintenance", "Insurance"],
    "Cleaning & Maintenance": ["Janitorial", "Landscaping", "Repairs", "Pest Control"],
    "Subscriptions": ["News & Media", "Industry Reports", "CRM", "Data Services"],
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_txn_id(date_str, amount, desc):
    raw = f"{date_str}|{amount}|{desc}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _insert_txn(c, txn_id, date_str, amount_cents, desc, category, account):
    """Insert a transaction row. Returns True if inserted, False on duplicate."""
    amount_dollars = amount_cents / 100.0
    try:
        c.execute(
            "INSERT INTO transactions"
            " (transaction_id, date, description_raw, merchant_canonical, amount, amount_cents,"
            "  account, category, source_filename, imported_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (txn_id, date_str, desc, desc, amount_dollars, int(amount_cents),
             account, category, "demo", datetime.now().isoformat()),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def seed_transactions(c, merchants, income_sources, account_map, large_txns, today, start):
    """Seed expense and income transactions. Returns count inserted."""
    txn_count = 0
    total_days = (today - start).days

    # ── Expenses ──
    for category, merchant_list in merchants.items():
        for merchant_name, min_amt, max_amt in merchant_list:
            account = account_map.get(category, "Primary Checking")

            if category in ("Subscriptions", "Software"):
                # Monthly on a fixed day
                day = random.randint(1, 28)
                d = start
                while d <= today:
                    if d.day == day:
                        amount = round(random.uniform(min_amt, max_amt), 2)
                        tid = make_txn_id(d.isoformat(), -amount, merchant_name)
                        if _insert_txn(c, tid, d.isoformat(), -amount * 100, merchant_name, category, account):
                            txn_count += 1
                    d += timedelta(days=1)

            elif category in ("Insurance", "Utilities", "Housing", "Student Loans",
                              "Employee Benefits", "Cleaning & Maintenance",
                              "Vehicle & Fleet", "Charity"):
                # Monthly on a fixed day
                day = random.randint(5, 25)
                d = start
                while d <= today:
                    if d.day == day:
                        amount = round(random.uniform(min_amt, max_amt), 2)
                        tid = make_txn_id(d.isoformat(), -amount, merchant_name)
                        if _insert_txn(c, tid, d.isoformat(), -amount * 100, merchant_name, category, account):
                            txn_count += 1
                    d += timedelta(days=1)

            elif category in ("Professional Services", "Taxes", "Consulting", "Legal"):
                # Quarterly-ish
                for _ in range(random.randint(2, 4)):
                    d = start + timedelta(days=random.randint(0, total_days))
                    amount = round(random.uniform(min_amt, max_amt), 2)
                    tid = make_txn_id(d.isoformat(), -amount, merchant_name + str(random.random()))
                    if _insert_txn(c, tid, d.isoformat(), -amount * 100, merchant_name, category, account):
                        txn_count += 1

            else:
                # Variable frequency
                if category in ("Groceries",):
                    times_per_month = random.randint(4, 8)
                elif category in ("Dining", "Meals & Entertainment"):
                    times_per_month = random.randint(3, 6)
                elif category in ("Gas & Auto", "Travel"):
                    times_per_month = random.randint(2, 4)
                elif category == "Marketing":
                    times_per_month = random.randint(2, 3)
                else:
                    times_per_month = random.randint(1, 2)

                num_txns = int(times_per_month * total_days / 30)
                for _ in range(num_txns):
                    d = start + timedelta(days=random.randint(0, total_days))
                    amount = round(random.uniform(min_amt, max_amt), 2)
                    tid = make_txn_id(d.isoformat(), -amount, merchant_name + str(random.random()))
                    # Leave some uncategorized for review testing
                    cat = category if random.random() > 0.12 else None
                    if _insert_txn(c, tid, d.isoformat(), -amount * 100, merchant_name, cat, account):
                        txn_count += 1

    # ── Income ──
    for source_name, min_amt, max_amt in income_sources:
        if "DEPOSIT" in source_name or "WIRE" in source_name:
            # Biweekly payroll / regular client payments
            d = start
            while d <= today:
                if d.weekday() == 4 and (d - start).days % 14 < 7:
                    amount = round(random.uniform(min_amt, max_amt), 2)
                    tid = make_txn_id(d.isoformat(), amount, source_name + str(random.random()))
                    acct = account_map.get("_income", "Primary Checking")
                    if _insert_txn(c, tid, d.isoformat(), amount * 100, source_name, "Income", acct):
                        txn_count += 1
                d += timedelta(days=1)
        else:
            # Occasional
            for _ in range(random.randint(3, 8)):
                d = start + timedelta(days=random.randint(0, total_days))
                amount = round(random.uniform(min_amt, max_amt), 2)
                tid = make_txn_id(d.isoformat(), amount, source_name + str(random.random()))
                acct = account_map.get("_income", "Primary Checking")
                if _insert_txn(c, tid, d.isoformat(), amount * 100, source_name, "Income", acct):
                    txn_count += 1

    # ── Large one-off transactions (uncategorized) ──
    for name, amount in large_txns:
        d = start + timedelta(days=random.randint(0, total_days))
        tid = make_txn_id(d.isoformat(), amount, name + str(random.random()))
        if _insert_txn(c, tid, d.isoformat(), amount * 100, name, None, None):
            txn_count += 1

    return txn_count


def seed_accounts(c, accounts):
    """Seed account_balances rows. Returns count inserted."""
    count = 0
    for name, acct_type, balance, limit_cents, due_day, payment_cents, sort in accounts:
        try:
            c.execute(
                "INSERT INTO account_balances"
                " (account_name, balance_cents, balance_source, account_type,"
                "  credit_limit_cents, payment_due_day, payment_amount_cents, sort_order)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (name, balance, "manual", acct_type, limit_cents, due_day, payment_cents, sort),
            )
            count += 1
        except sqlite3.IntegrityError:
            pass
    return count


def seed_manual_recurring(c, recurring, accounts):
    """Seed manual_recurring rows. Returns count inserted."""
    # Build name→id map
    acct_ids = {}
    for row in c.execute("SELECT id, account_name FROM account_balances").fetchall():
        acct_ids[row[0] if isinstance(row, tuple) else row["account_name"]] = (
            row[1] if isinstance(row, tuple) else row["id"]
        )
    # Ugh, tuple mode — index based
    for row in c.execute("SELECT id, account_name FROM account_balances").fetchall():
        acct_ids[row[1]] = row[0]

    count = 0
    for acct_name, merchant, amount_cents, day in recurring:
        acct_id = acct_ids.get(acct_name)
        if not acct_id:
            continue
        try:
            c.execute(
                "INSERT INTO manual_recurring (account_id, merchant, amount_cents, day_of_month)"
                " VALUES (?,?,?,?)",
                (acct_id, merchant, amount_cents, day),
            )
            count += 1
        except sqlite3.IntegrityError:
            pass
    return count


def seed_categories(c, extra_categories):
    """Seed extra categories and subcategories. Returns (cat_count, sub_count)."""
    now = datetime.now().isoformat()
    cat_count = 0
    sub_count = 0
    for category, subcategories in extra_categories.items():
        try:
            c.execute(
                "INSERT OR IGNORE INTO categories (name, created_at) VALUES (?,?)",
                (category, now),
            )
            cat_count += 1
        except sqlite3.IntegrityError:
            pass
        for sub in subcategories:
            try:
                c.execute(
                    "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) VALUES (?,?,?)",
                    (category, sub, now),
                )
                sub_count += 1
            except sqlite3.IntegrityError:
                pass
    return cat_count, sub_count


def seed_entity(entity_key, merchants, income_sources, account_map,
                accounts_def, recurring_def, large_txns, extra_categories):
    """Seed a complete entity with transactions, accounts, and recurring."""
    init_db(entity_key)
    db_path = get_db_path(entity_key)
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    # Wipe existing data for clean re-seed
    existing = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if existing > 0:
        print(f"  {entity_key}: wiping {existing} existing transactions for fresh seed")
        c.execute("DELETE FROM transactions")
        c.execute("DELETE FROM account_balances")
        c.execute("DELETE FROM manual_recurring")
        c.execute("DELETE FROM categories")
        c.execute("DELETE FROM subcategories")
        conn.commit()

    today = datetime.now().date()
    start = today - timedelta(days=180)  # 6 months of data

    cat_count, sub_count = seed_categories(c, extra_categories)
    txn_count = seed_transactions(c, merchants, income_sources, account_map, large_txns, today, start)
    acct_count = seed_accounts(c, accounts_def)
    rec_count = seed_manual_recurring(c, recurring_def, accounts_def)

    conn.commit()
    conn.close()
    print(f"  {entity_key}: seeded {txn_count} txns, {acct_count} accounts, {rec_count} recurring, {cat_count} categories, {sub_count} subcategories")


if __name__ == "__main__":
    print("Seeding demo data...")

    seed_entity(
        "personal",
        PERSONAL_MERCHANTS, PERSONAL_INCOME, PERSONAL_ACCOUNT_MAP,
        PERSONAL_ACCOUNTS, PERSONAL_RECURRING, PERSONAL_LARGE_TXNS,
        PERSONAL_EXTRA_CATEGORIES,
    )

    seed_entity(
        "company",
        BUSINESS_MERCHANTS, BUSINESS_INCOME,
        {**BUSINESS_ACCOUNT_MAP, "_income": "Business Checking"},
        BUSINESS_ACCOUNTS, BUSINESS_RECURRING, BUSINESS_LARGE_TXNS,
        BUSINESS_EXTRA_CATEGORIES,
    )

    print("Done!")
