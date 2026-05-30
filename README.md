# 🏦 Loan Eligibility Checker

A beginner-friendly Python project that checks home-loan eligibility based on applicant financial details. Includes a **REST API** (Flask) and a **CLI** interface, with records stored in a local **JSON** file.

---

## 📂 Project Structure

```
loanchecker/
├── README.md               ← You are here
├── requirements.txt        ← Python dependencies
├── run.py                  ← Start the API server
├── cli.py                  ← Command-line interface
├── data/
│   └── applicants.json     ← Saved applicant records (sample data included)
└── app/
    ├── __init__.py          ← Package init
    ├── eligibility.py       ← Core calculation logic (EMI, DTI, eligibility)
    ├── storage.py           ← JSON file read/write helpers
    └── api.py               ← Flask REST API endpoints
```

---

## 🚀 Setup & Run (VS Code)

### 1. Open the project folder
```bash
cd c:\PROJECTS\loanchecker
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4a. Run the API server
```bash
python run.py
```
The server starts at **http://127.0.0.1:5000**

### 4b. Run the CLI (alternative)
```bash
python cli.py
```

---

## 🔌 API Endpoints

| Method | Endpoint                   | Description                        |
|--------|----------------------------|------------------------------------|
| POST   | `/api/check`               | Submit details & check eligibility |
| GET    | `/api/applicants`          | List all saved applicants          |
| GET    | `/api/applicants/<id>`     | Get a single applicant by ID       |
| PUT    | `/api/applicants/<id>`     | Update applicant & re-check        |
| DELETE | `/api/applicants/<id>`     | Delete an applicant record         |

### Example — Check Eligibility (curl)

```bash
curl -X POST http://127.0.0.1:5000/api/check ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Amit Kumar\",\"monthly_income\":90000,\"existing_emi\":5000,\"property_value\":5000000,\"desired_loan_amount\":4000000,\"loan_tenure_years\":20,\"interest_rate\":8.5}"
```

### Example — List All Applicants
```bash
curl http://127.0.0.1:5000/api/applicants
```

### Example — Delete an Applicant
```bash
curl -X DELETE http://127.0.0.1:5000/api/applicants/sample-001
```

---

## 🧮 Eligibility Logic

| Check                     | Rule                                       |
|---------------------------|--------------------------------------------|
| **EMI Calculation**       | Standard reducing-balance formula           |
| **Debt-to-Income (DTI)**  | (Existing EMI + New EMI) / Income × 100     |
| **Credit Category**       | ≤36% → Good · 37-50% → Average · >50% → Risky |
| **Loan-to-Value (LTV)**   | Loan amount must be ≤ 90% of property value |
| **Max Eligible Loan**     | Computed from max affordable EMI at 50% DTI |

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Flask** — lightweight REST API framework
- **JSON** — flat-file data storage
- **uuid** — unique record IDs (built-in)

---

## 📄 License

This project is for educational / portfolio purposes.
