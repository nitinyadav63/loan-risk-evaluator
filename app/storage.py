"""
storage.py — MongoDB Storage
===============================
Connects to a MongoDB database to store applicant records.
Uses the 'MONGO_URI' from environment variables.
"""

import os
import logging
from typing import List, Dict, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

# --- Database Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "loanchecker"
COLLECTION_NAME = "applicants"

# Initialize Client
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Simple check to verify connection
    client.server_info() 
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error(f"Could not connect to MongoDB: {e}")
    collection = None

# -----------------------------------------------------------
# READ — Get records (optionally filtered by session)
# -----------------------------------------------------------
def get_all_applicants(session_id: Optional[str] = None) -> List[Dict]:
    """Return the list of applicant dicts from MongoDB."""
    if collection is None: return []
    
    query = {"session_id": session_id} if session_id else {}
    cursor = collection.find(query, {'_id': 0})
    return list(cursor)


# -----------------------------------------------------------
# READ — Get one record by ID
# -----------------------------------------------------------
def get_applicant_by_id(applicant_id: str) -> Optional[Dict]:
    """Return a single applicant dict, or None if not found."""
    if collection is None: return None
    
    return collection.find_one({"id": applicant_id}, {'_id': 0})


# -----------------------------------------------------------
# CREATE — Save a new record
# -----------------------------------------------------------
def save_applicant(record: dict) -> dict:
    """Insert a new applicant record into MongoDB."""
    if collection is None:
        logger.error("Database not connected. Failed to save.")
        return record
        
    collection.insert_one(record.copy())
    logger.info("Inserted new applicant into MongoDB: %s", record.get("id"))
    return record


# -----------------------------------------------------------
# UPDATE — Replace an existing record by ID
# -----------------------------------------------------------
def update_applicant(applicant_id: str, updated: dict) -> Optional[Dict]:
    """
    Find the record with the given ID and replace it.
    """
    if collection is None: return None
    
    updated["id"] = applicant_id
    result = collection.replace_one({"id": applicant_id}, updated)
    
    if result.matched_count > 0:
        logger.info("Updated applicant in MongoDB: %s", applicant_id)
        return updated
    return None


# -----------------------------------------------------------
# DELETE — Remove a record by ID
# -----------------------------------------------------------
def delete_applicant(applicant_id: str) -> bool:
    """
    Remove the applicant with the given ID.
    """
    if collection is None: return False
    
    result = collection.delete_one({"id": applicant_id})
    if result.deleted_count > 0:
        logger.info("Deleted applicant from MongoDB: %s", applicant_id)
        return True
    return False
