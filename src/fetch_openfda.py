#!/usr/bin/env python3
"""
Fetch recent adverse event reports from OpenFDA and write a dated snapshot CSV.

Usage:
  - Locally (not required): OPENFDA_API_KEY=xxx python src/fetch_openfda.py
  - In GitHub Actions: set OPENFDA_API_KEY as a secret (optional)
"""

import os
import requests
import pandas as pd
from datetime import datetime

# Configurable parameters
BASE_URL = "https://api.fda.gov/drug/event.json"
# Example query: look for reports mentioning "overdose" or common reactions; adjust later
QUERY = 'patient.reaction.reactionmeddrapt:overdose'
LIMIT = 100  # OpenFDA default max is 100 per request

def fetch_openfda(query=QUERY, limit=LIMIT):
    params = {"search": query, "limit": limit}
    api_key = os.getenv("OPENFDA_API_KEY")
    if api_key:
        params["api_key"] = api_key
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def normalize_openfda(payload):
    rows = []
    for item in payload.get("results", []):
        report_id = item.get("safetyreportid")
        receipt_date = item.get("receiptdate")
        patient = item.get("patient", {}) or {}
        drugs = patient.get("drug", []) or []
        reactions = patient.get("reaction", []) or []
        # Flatten: one row per drug with concatenated reactions
        reaction_list = [r.get("reactionmeddrapt", "") for r in reactions]
        reactions_text = ";".join([r for r in reaction_list if r])
        for d in drugs:
            rows.append({
                "report_id": report_id,
                "receipt_date": receipt_date,
                "drug": d.get("medicinalproduct"),
                "drug_role": d.get("drugcharacterization"),
                "reactions": reactions_text
            })
    if not rows:
        return pd.DataFrame(columns=["report_id","receipt_date","drug","drug_role","reactions"])
    return pd.DataFrame(rows)

def write_snapshot(df):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = "data"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"live_snapshot_{ts}.csv")
    df.to_csv(out_path, index=False)
    print("Wrote snapshot:", out_path)
    return out_path

def main():
    try:
        payload = fetch_openfda()
    except Exception as e:
        print("Error fetching OpenFDA:", str(e))
        return
    df = normalize_openfda(payload)
    print("Fetched rows:", len(df))
    write_snapshot(df)

if __name__ == "__main__":
    main()

