#!/usr/bin/env python3
"""Insert budget line items into personal.sqlite on production."""
import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", "./local_state")
DB_PATH = os.path.join(DATA_DIR, "personal.sqlite")

BUDGET_ITEMS = [
    ("Housing", 1110000),
    ("Ranch", 819200),
    ("Fees", 237500),
    ("Food", 222100),
    ("Home", 167700),
    ("Insurance", 117200),
    ("Utilities", 99400),
    ("Entertainment", 94300),
    ("Shopping", 90100),
    ("Household", 88800),
    ("Student Loans", 71600),
    ("Clothing", 68600),
    ("Retirement", 55000),
    ("Abuelitos", 53300),
    ("Childcare", 51300),
    ("Transportation", 35600),
    ("Healthcare", 30600),
    ("Health & Beauty", 26300),
    ("LL Expense", 23200),
    ("Storage", 17900),
    ("Electronics", 9300),
    ("Pets", 4700),
    ("Fitness", 4300),
    ("Supplies", 3300),
    ("Kids", 3300),
]

# New categories that may not exist on production yet
NEW_CATEGORIES = [
    "Abuelitos",
    "Childcare",
    "Fitness",
]

NEW_SUBCATEGORIES = [
    ("Abuelitos", "General"),
    ("Abuelitos", "Stipend"),
    ("Childcare", "General"),
    ("Fitness", "General"),
    ("Shopping", "ATM Withdrawal"),
    ("Shopping", "Kids"),
    ("Entertainment", "Kids"),
    ("Clothing", "Kristine"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create new categories
    for cat in NEW_CATEGORIES:
        c.execute("SELECT id FROM categories WHERE name = ?", (cat,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO categories (name, created_at) VALUES (?, datetime('now'))",
                (cat,),
            )
            print(f"  Created category: {cat}")

    # Create new subcategories
    for cat, sub in NEW_SUBCATEGORIES:
        c.execute(
            "SELECT id FROM subcategories WHERE category_name = ? AND name = ?",
            (cat, sub),
        )
        if not c.fetchone():
            c.execute(
                "INSERT INTO subcategories (category_name, name, created_at) VALUES (?, ?, datetime('now'))",
                (cat, sub),
            )
            print(f"  Created subcategory: {cat}/{sub}")

    # Insert budget items (skip if already exist)
    inserted = 0
    skipped = 0
    for category, cents in BUDGET_ITEMS:
        c.execute("SELECT id FROM budget_items WHERE category = ?", (category,))
        if c.fetchone():
            skipped += 1
            continue
        c.execute(
            "INSERT INTO budget_items (category, monthly_budget_cents) VALUES (?, ?)",
            (category, cents),
        )
        print(f"  ADD  {category} — ${cents / 100:,.0f}/mo")
        inserted += 1

    conn.commit()
    print(f"\nBudget items: {inserted} inserted, {skipped} skipped")
    conn.close()


if __name__ == "__main__":
    main()
