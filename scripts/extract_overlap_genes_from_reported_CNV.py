import os
import sys
import requests
import pandas as pd

# -----------------------------
# 0️⃣ Get EMG number from argument
# -----------------------------
if len(sys.argv) != 2:
    print("Usage: python emg_extract.py EMG_NUMBER")
    sys.exit(1)

EMG_NUMBER = sys.argv[1]
HOSTNAME = "pch-production"

# -----------------------------
# 1️⃣ Login
# -----------------------------
USERNAME = os.environ.get("EMG_USERNAME")
PASSWORD = os.environ.get("EMG_PASSWORD")

if not USERNAME or not PASSWORD:
    raise Exception("Please set EMG_USERNAME and EMG_PASSWORD as environment variables.")

login_url = f"https://{HOSTNAME}.emg.illumina.com/api/auth/v2/api_login/"
payload = {"username": USERNAME, "password": PASSWORD}

resp = requests.post(login_url, json=payload)
resp.raise_for_status()

token_data = resp.json()
access_token = token_data.get("access_token")
token_type = token_data.get("token_type")

if not access_token:
    raise Exception(f"Login failed: {token_data}")

AUTH_HEADER = {
    "Authorization": f"{token_type} {access_token}",
    "Accept": "*/*"
}

# -----------------------------
# 2️⃣ Get gene list + geneListName
# -----------------------------
case_url = f"https://{HOSTNAME}.emg.illumina.com/api/test/{EMG_NUMBER}/"
case_response = requests.get(case_url, headers=AUTH_HEADER)
case_response.raise_for_status()
case_data = case_response.json()

geneListName = case_data.get("geneListName")
panel_genes = {gene["name"] for gene in case_data.get("genes", [])}

# -----------------------------
# 3️⃣ Get variants and filter "in_report"
# -----------------------------
export_url = f"https://{HOSTNAME}.emg.illumina.com/api/test/{EMG_NUMBER}/export/"
response = requests.get(export_url, headers=AUTH_HEADER)
response.raise_for_status()
data = response.json()

results = []

for variant in data.get("variants", []):
    tag = variant.get("tag", {})
    tag_value = tag.get("value", "")

    if tag_value.lower() == "in_report":
        gene_name = variant.get("gene_name", "")
        variant_details = variant.get("variant_details")

        variant_genes = {g.strip() for g in gene_name.split(",") if g.strip()}
        overlap = variant_genes & panel_genes

        if overlap:
            results.append({
                "EMG_Number": EMG_NUMBER,
                "geneListName": geneListName,
                "overlapping_genes": ", ".join(sorted(overlap)),
                "variant_details": variant_details
            })

# -----------------------------
# 4️⃣ Export to CSV (one directory up)
# -----------------------------

# Get directory where script lives (scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (project/)
parent_dir = os.path.dirname(script_dir)

# Define output directory path
output_dir = os.path.join(parent_dir, "output")

# Create output folder if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define output file
output_path = os.path.join(output_dir, "results.csv")

if results:
    df = pd.DataFrame(results)
    df = df[["EMG_Number", "geneListName", "overlapping_genes", "variant_details"]]
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
else:
    print("No overlapping in_report variants found.")
