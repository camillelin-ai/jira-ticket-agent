"""
Run this once to discover the custom field IDs for your Jira instance.
Output tells you what to put in config/ec.json and config/avp.json.

Usage:
    python scripts/fetch_field_ids.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://appliedintuition.atlassian.net"
EMAIL    = os.environ["JIRA_EMAIL"]
API_TOKEN = os.environ["JIRA_API_TOKEN"]

auth    = (EMAIL, API_TOKEN)
headers = {"Accept": "application/json"}

response = requests.get(f"{BASE_URL}/rest/api/3/field", auth=auth, headers=headers)
response.raise_for_status()

fields = response.json()

keywords = ["sprint", "acceptance", "engagement", "story point", "eng sprint"]

print("Fields matching your keywords:\n")
for field in fields:
    name = field.get("name", "").lower()
    if any(k in name for k in keywords):
        print(f"  Name:  {field['name']}")
        print(f"  ID:    {field['id']}")
        print()

print("All custom fields (for reference):\n")
for field in fields:
    if field["id"].startswith("customfield_"):
        print(f"  {field['id']:<30} {field['name']}")
