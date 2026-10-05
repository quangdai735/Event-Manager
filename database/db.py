import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

print("Đường dẫn .env:", ENV_FILE)
print(".env tồn tại:", ENV_FILE.exists())

load_dotenv(dotenv_path=ENV_FILE)

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["event_db"]
print("MONGO_URL:", MONGO_URL)
print("Database:", db.name)
print("Danh sách các collection hiện có:", db.list_collection_names())
users = db["users"]
events = db["events"]
tickets = db["tickets"]
categories = db["categories"]

# ===== AUTO CATEGORY =====
default_categories = ["Âm nhạc", "Thể thao", "Workshop", "Hội thảo", "Triển lãm"]

for c in default_categories:
    if not categories.find_one({"name": c}):
        categories.insert_one({"name": c})