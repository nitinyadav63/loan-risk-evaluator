"""
api.py — Final Version with Privacy Sessions
=============================================
"""

import os
import uuid
import logging
from functools import wraps
from typing import Optional, Union
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

from .eligibility import check_eligibility
from .storage import (
    get_all_applicants,
    get_applicant_by_id,
    save_applicant,
    update_applicant,
    delete_applicant,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())
API_KEY = os.environ.get("LOAN_API_KEY", None)

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if API_KEY is None: return f(*args, **kwargs)
        provided_key = request.headers.get("X-API-Key", "")
        if provided_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
@app.route("/googled17c5ddf7a1c7db6.html")
def google_verify():
    return send_from_directory(
        os.path.join(os.getcwd(), "static"),
        "googled17c5ddf7a1c7db6.html"
    )

@app.route("/api/health", methods=["GET"])
def health_check():
    from .storage import get_collection
    db_status = "Connected" if get_collection() is not None else "Disconnected"
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "environment": "production" if os.environ.get("VERCEL") else "development"
    }), 200

@app.errorhandler(Exception)
def handle_exception(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException): return e
    logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "details": str(e) if os.environ.get("FLASK_DEBUG") == "1" else "Contact administrator"
    }), 500

# ============================================================
# API Endpoints
# ============================================================

@app.route("/api/check", methods=["POST"])
@require_api_key
def api_check_eligibility():
    data = request.get_json(silent=True)
    if not data: return jsonify({"error": "Invalid JSON"}), 400

    # Capture session ID for privacy
    session_id = data.get("session_id", "anonymous")

    result = check_eligibility(data)
    record = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,  # Link record to this user's session
        "name": data["name"],
        "monthly_income": data["monthly_income"],
        "existing_emi": data["existing_emi"],
        "property_value": data["property_value"],
        "desired_loan_amount": data["desired_loan_amount"],
        "loan_tenure_years": data["loan_tenure_years"],
        "interest_rate": data["interest_rate"],
        "result": result,
    }
    save_applicant(record)
    return jsonify(record), 201

@app.route("/api/applicants", methods=["GET"])
@require_api_key
def api_list_applicants():
    # Filter by the dashboard's session ID
    sid = request.args.get("session_id")
    return jsonify(get_all_applicants(sid)), 200

@app.route("/api/applicants/<applicant_id>", methods=["DELETE"])
@require_api_key
def api_delete_applicant(applicant_id):
    if not delete_applicant(applicant_id):
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200
