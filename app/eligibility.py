"""
eligibility.py — Core Loan Eligibility Logic
=============================================
This module contains pure functions that:
  1. Calculate the monthly EMI using the standard reducing-balance formula.
  2. Compute the Debt-to-Income (DTI) ratio.
  3. Determine a simple credit-score category (Good / Average / Risky).
  4. Find the maximum loan amount the applicant can afford.
  5. Return a final eligibility verdict with remarks.

No database or file I/O happens here — that is handled by storage.py.
"""

import math


# -----------------------------------------------------------
# 1. EMI Calculator  (Reducing-Balance Method)
# -----------------------------------------------------------
def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> float:
    """
    Calculate the Equated Monthly Instalment (EMI).

    Formula:  EMI = P × r × (1+r)^n  /  ((1+r)^n − 1)
      where   P = principal loan amount
              r = monthly interest rate  (annual_rate / 12 / 100)
              n = total number of monthly instalments

    Returns the EMI rounded to the nearest rupee.

    Raises ValueError for invalid inputs (zero tenure, negative principal, etc.).
    """
    # Validate inputs
    if tenure_years <= 0:
        raise ValueError("Loan tenure must be at least 1 year")
    if principal <= 0:
        raise ValueError("Principal must be a positive number")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")

    # Monthly interest rate
    r = annual_rate / 12 / 100

    # Total number of monthly instalments
    n = tenure_years * 12

    # Edge case: 0 % interest
    if r == 0:
        return round(principal / n)

    emi = principal * r * math.pow(1 + r, n) / (math.pow(1 + r, n) - 1)
    return round(emi)


# -----------------------------------------------------------
# 2. Debt-to-Income Ratio
# -----------------------------------------------------------
def calculate_dti(monthly_income: float, existing_emi: float, new_emi: float) -> float:
    """
    Debt-to-Income ratio (%) =
        (existing EMI + new proposed EMI) / monthly income × 100

    A lower DTI is better.  Generally:
        ≤ 36 %  →  Good
        37-50 % →  Average
        > 50 %  →  Risky
    """
    if monthly_income <= 0:
        return 100.0  # Treat zero/negative income as maximum risk

    dti = ((existing_emi + new_emi) / monthly_income) * 100
    return round(dti, 2)


# -----------------------------------------------------------
# 3. Credit-Score Category
# -----------------------------------------------------------
def credit_category(dti: float) -> str:
    """
    Return a simple risk label based on the DTI ratio.
    """
    if dti <= 36:
        return "Good"
    elif dti <= 50:
        return "Average"
    else:
        return "Risky"


# -----------------------------------------------------------
# 4. Maximum Eligible Loan Amount
# -----------------------------------------------------------
def max_eligible_loan(monthly_income: float, existing_emi: float,
                      annual_rate: float, tenure_years: int,
                      max_dti: float = 50.0) -> float:
    """
    Work backwards from the maximum affordable EMI to find the
    largest loan the applicant could service.

    max_affordable_emi = (monthly_income × max_dti / 100) − existing_emi
    Then invert the EMI formula to get the principal.
    """
    if tenure_years <= 0:
        return 0.0

    r = annual_rate / 12 / 100
    n = tenure_years * 12
    max_emi = (monthly_income * max_dti / 100) - existing_emi

    if max_emi <= 0:
        return 0.0

    if r == 0:
        return round(max_emi * n)

    principal = max_emi * (math.pow(1 + r, n) - 1) / (r * math.pow(1 + r, n))
    return round(principal)


# -----------------------------------------------------------
# 5. Full Eligibility Check  (brings everything together)
# -----------------------------------------------------------
def check_eligibility(applicant: dict) -> dict:
    """
    Accept a dict of applicant details and return a result dict.

    Expected keys in `applicant`:
        monthly_income, existing_emi, property_value,
        desired_loan_amount, loan_tenure_years, interest_rate

    Returns:
        {
            eligible: bool,
            monthly_emi: int,
            debt_to_income_ratio: float,
            credit_category: str,
            max_eligible_loan: float,
            remarks: str
        }
    """
    # --- Extract inputs ---
    income       = applicant["monthly_income"]
    existing_emi = applicant["existing_emi"]
    property_val = applicant["property_value"]
    loan_amount  = applicant["desired_loan_amount"]
    tenure       = applicant["loan_tenure_years"]
    rate         = applicant["interest_rate"]

    # --- Calculations ---
    try:
        emi = calculate_emi(loan_amount, rate, tenure)
    except ValueError:
        # Fallback for invalid tenure during cross-calculation
        emi = 0
        
    dti = calculate_dti(income, existing_emi, emi)
    category = credit_category(dti)
    max_loan = max_eligible_loan(income, existing_emi, rate, tenure)

    # --- Eligibility rules ---
    # Rule 1: DTI must not exceed 50 %
    # Rule 2: Loan amount must not exceed 90 % of property value (LTV cap)
    if property_val <= 0:
        ltv = 100.0  # Invalid property value → treat as over-limit
    else:
        ltv = (loan_amount / property_val * 100)

    eligible = (dti <= 50) and (ltv <= 90)

    # --- Build remarks ---
    remarks_parts = []
    if eligible:
        remarks_parts.append("Eligible.")
    else:
        remarks_parts.append("Not Eligible.")

    if dti > 50:
        remarks_parts.append(
            f"Debt-to-income ratio ({dti}%) exceeds the 50% threshold."
        )
    elif dti > 36:
        remarks_parts.append(
            "Debt-to-income ratio is moderate — consider reducing existing EMIs for a better rate."
        )
    else:
        remarks_parts.append(
            "Strong financial profile with no existing debt."
            if existing_emi == 0 else
            "Healthy debt-to-income ratio."
        )

    if ltv > 90:
        remarks_parts.append(
            f"Loan-to-value ratio ({ltv:.1f}%) exceeds the 90% cap."
        )

    if property_val <= 0:
        remarks_parts.append("Property value must be greater than zero.")

    return {
        "eligible":              eligible,
        "monthly_emi":           emi,
        "debt_to_income_ratio":  dti,
        "credit_category":       category,
        "max_eligible_loan":     max_loan,
        "remarks":               " ".join(remarks_parts),
    }
