"""
cli.py — Command-Line Interface for Loan Eligibility Checker
=============================================================
Run this file directly to use the checker from the terminal:

    python cli.py

The CLI lets you:
  1. Check eligibility by entering applicant details
  2. View all saved applicant records
  3. View a single applicant by ID
  4. Delete an applicant record
"""

import uuid
from app.eligibility import check_eligibility
from app.storage import (
    get_all_applicants,
    get_applicant_by_id,
    save_applicant,
    delete_applicant,
)


# -----------------------------------------------------------
# Helper — Read a number from the user with validation
# -----------------------------------------------------------
def _input_number(prompt: str, cast=float, min_val=None, max_val=None) -> float | int:
    """Keep asking until the user enters a valid number within range."""
    while True:
        raw = input(prompt).strip()
        try:
            value = cast(raw)
            if min_val is not None and value < min_val:
                print(f"  ⚠  Value must be at least {min_val}.\n")
                continue
            if max_val is not None and value > max_val:
                print(f"  ⚠  Value must be at most {max_val}.\n")
                continue
            return value
        except ValueError:
            print(f"  ⚠  Please enter a valid number.\n")


# -----------------------------------------------------------
# Option 1 — Check Eligibility
# -----------------------------------------------------------
def do_check():
    """Collect inputs, run the engine, display the result, and save."""
    print("\n" + "─" * 50)
    print("  Enter Applicant Details")
    print("─" * 50)

    name          = input("  Name                : ").strip()[:200] or "Unknown"
    income        = _input_number("  Monthly Income (₹)  : ", min_val=0, max_val=1_000_000_000)
    existing_emi  = _input_number("  Existing EMI (₹)    : ", min_val=0, max_val=1_000_000_000)
    property_val  = _input_number("  Property Value (₹)  : ", min_val=1, max_val=100_000_000_000)
    loan_amount   = _input_number("  Desired Loan Amt (₹): ", min_val=1, max_val=100_000_000_000)
    tenure        = _input_number("  Loan Tenure (years) : ", cast=int, min_val=1, max_val=40)
    rate          = _input_number("  Interest Rate (%)   : ", min_val=0.01, max_val=50)

    applicant = {
        "name":                name,
        "monthly_income":      income,
        "existing_emi":        existing_emi,
        "property_value":      property_val,
        "desired_loan_amount": loan_amount,
        "loan_tenure_years":   tenure,
        "interest_rate":       rate,
    }

    # Run eligibility check
    result = check_eligibility(applicant)

    # Display result
    print("\n" + "═" * 50)
    print("  ELIGIBILITY RESULT")
    print("═" * 50)
    print(f"  Applicant       : {name}")
    print(f"  Eligible        : {'✅ YES' if result['eligible'] else '❌ NO'}")
    print(f"  Monthly EMI     : ₹{result['monthly_emi']:,}")
    print(f"  DTI Ratio       : {result['debt_to_income_ratio']}%")
    print(f"  Credit Category : {result['credit_category']}")
    print(f"  Max Eligible    : ₹{result['max_eligible_loan']:,}")
    print(f"  Remarks         : {result['remarks']}")
    print("═" * 50)

    # Save to JSON (full UUID)
    record = {
        "id": str(uuid.uuid4()),
        **applicant,
        "result": result,
    }
    save_applicant(record)
    print(f"\n  ✔  Record saved with ID: {record['id']}\n")


# -----------------------------------------------------------
# Option 2 — View All Applicants
# -----------------------------------------------------------
def do_list():
    """Print a table of all saved applicants."""
    records = get_all_applicants()
    if not records:
        print("\n  No records found.\n")
        return

    print("\n" + "─" * 80)
    print(f"  {'ID':<12} {'Name':<20} {'Eligible':<10} {'EMI':>10} {'DTI':>8} {'Category':<10}")
    print("─" * 80)
    for r in records:
        res = r.get("result", {})
        elig = "YES" if res.get("eligible") else "NO"
        emi  = f"₹{res.get('monthly_emi', 0):,}"
        dti  = f"{res.get('debt_to_income_ratio', 0)}%"
        cat  = res.get("credit_category", "N/A")
        display_id = r['id'][:12] if len(r.get('id', '')) > 12 else r['id']
        print(f"  {display_id:<12} {r['name']:<20} {elig:<10} {emi:>10} {dti:>8} {cat:<10}")
    print("─" * 80 + "\n")


# -----------------------------------------------------------
# Option 3 — View One Applicant
# -----------------------------------------------------------
def do_view_one():
    """Look up a single applicant by ID and display full details."""
    aid = input("\n  Enter Applicant ID: ").strip()
    record = get_applicant_by_id(aid)
    if not record:
        print(f"  ⚠  No applicant found with ID '{aid}'\n")
        return

    print("\n" + "═" * 50)
    for key, value in record.items():
        if key == "result":
            print(f"  {'─'*46}")
            for rk, rv in value.items():
                print(f"  {rk:<25}: {rv}")
        else:
            print(f"  {key:<25}: {value}")
    print("═" * 50 + "\n")


# -----------------------------------------------------------
# Option 4 — Delete an Applicant
# -----------------------------------------------------------
def do_delete():
    """Delete an applicant record by ID."""
    aid = input("\n  Enter Applicant ID to delete: ").strip()
    if delete_applicant(aid):
        print(f"  ✔  Applicant '{aid}' deleted.\n")
    else:
        print(f"  ⚠  No applicant found with ID '{aid}'\n")


# -----------------------------------------------------------
# Main Menu Loop
# -----------------------------------------------------------
def main():
    print("\n" + "═" * 50)
    print("  LOAN ELIGIBILITY CHECKER  —  CLI")
    print("═" * 50)

    while True:
        print("  1.  Check Eligibility")
        print("  2.  View All Applicants")
        print("  3.  View One Applicant")
        print("  4.  Delete an Applicant")
        print("  5.  Exit")
        choice = input("\n  Choose an option (1-5): ").strip()

        if   choice == "1": do_check()
        elif choice == "2": do_list()
        elif choice == "3": do_view_one()
        elif choice == "4": do_delete()
        elif choice == "5":
            print("\n  Goodbye! 👋\n")
            break
        else:
            print("  ⚠  Invalid choice. Please enter 1–5.\n")


if __name__ == "__main__":
    main()
