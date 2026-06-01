"""
run.py — Entry Point for the Loan Eligibility Checker API
==========================================================
Start the Flask development server:

    python run.py

The server will be available at http://127.0.0.1:5000
"""

import os
from app.api import app

if __name__ == "__main__":
    # Read debug flag from environment — NEVER default to True in production
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("=" * 55)
    print("  Loan Eligibility Checker API")
    print(f"  Running at  ->  http://127.0.0.1:5000")
    print(f"  Debug mode  ->  {'ON [WARNING]' if debug_mode else 'OFF [OK]'}")
    if os.environ.get("LOAN_API_KEY"):
        print("  Auth        ->  API key required [OK]")
    else:
        print("  Auth        ->  OPEN (set LOAN_API_KEY to secure)")
    print("=" * 55)
    app.run(debug=debug_mode, port=5000)
