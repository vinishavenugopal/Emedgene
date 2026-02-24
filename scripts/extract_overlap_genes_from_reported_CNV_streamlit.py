import os
from pathlib import Path
import pandas as pd
import requests
import streamlit as st
import time

HOSTNAME = "pch-production"

# --------------------------
# Helper functions
# --------------------------
def login(username: str, password: str) -> dict:
    login_url = f"https://{HOSTNAME}.emg.illumina.com/api/auth/v2/api_login/"
    payload = {"username": username, "password": password}

    response = requests.post(login_url, json=payload, timeout=30)
    response.raise_for_status()
    token_data = response.json()
    access_token = token_data.get("access_token")
    token_type = token_data.get("token_type")

    if not access_token:
        raise RuntimeError(f"Login failed: {token_data}")

    return {"Authorization": f"{token_type} {access_token}", "Accept": "*/*"}


def extract_overlap_variants(emg_number: str, auth_header: dict, progress_callback=None):
    # Step 1: Fetch case metadata
    if progress_callback:
        progress_callback("Fetching case metadata...")
    case_url = f"https://{HOSTNAME}.emg.illumina.com/api/test/{emg_number}/"
    case_response = requests.get(case_url, headers=auth_header, timeout=30)
    case_response.raise_for_status()
    case_data = case_response.json()

    gene_list_name = case_data.get("geneListName")
    panel_genes = {gene["name"] for gene in case_data.get("genes", [])}

    # Step 2: Fetch export variants
    if progress_callback:
        progress_callback("Fetching variants export...")
    export_url = f"https://{HOSTNAME}.emg.illumina.com/api/test/{emg_number}/export/"
    response = requests.get(export_url, headers=auth_header, timeout=60)
    response.raise_for_status()
    data = response.json()

    results = []
    variants = data.get("variants", [])
    total_variants = len(variants)

    # Step 3: Process variants with progress
    for i, variant in enumerate(variants, 1):
        if progress_callback:
            progress_callback(f"Processing variant {i}/{total_variants}...")

        tag_value = variant.get("tag", {}).get("value", "")
        if tag_value.lower() != "in_report":
            continue

        gene_name = variant.get("gene_name", "")
        variant_genes = {g.strip() for g in gene_name.split(",") if g.strip()}
        overlap = variant_genes & panel_genes

        if overlap:
            results.append(
                {
                    "EMG_Number": emg_number,
                    "geneListName": gene_list_name,
                    "overlapping_genes": ", ".join(sorted(overlap)),
                    "variant_details": variant.get("Variant_details"),
                }
            )

    return pd.DataFrame(results)


def save_results(df: pd.DataFrame) -> Path:
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "results.csv"

    if not df.empty:
        ordered_df = df[["EMG_Number", "geneListName", "overlapping_genes", "variant_details"]]
        ordered_df.to_csv(output_path, index=False)

    return output_path

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="EMG In-Report Variant Extractor", layout="wide")
st.title("EMG In-Report Variant Extractor")
st.markdown("Extract overlapping in-report genes and save results to CSV.")

with st.sidebar:
    st.header("Connection")
    username = st.text_input("EMG Username", value=os.environ.get("EMG_USERNAME", ""))
    password = st.text_input("EMG Password", value=os.environ.get("EMG_PASSWORD", ""), type="password")

emg_number = st.text_input("EMG Number", placeholder="EMG824233283")

progress_text = st.empty()
progress_bar = st.progress(0)

if st.button("Run Extraction"):
    if not username or not password:
        st.error("Please provide EMG_USERNAME and EMG_PASSWORD.")
    elif not emg_number:
        st.error("Please provide an EMG number.")
    else:
        try:
            # Step 1: Login
            progress_text.text("Authenticating...")
            auth_header = login(username, password)
            progress_bar.progress(10)

            # Step 2: Fetch & process
            def callback(message):
                progress_text.text(message)
            df = extract_overlap_variants(emg_number.strip(), auth_header, progress_callback=callback)
            progress_bar.progress(90)

            # Step 3: Save results
            output_path = save_results(df)
            progress_bar.progress(100)
            progress_text.text("Done!")

            if df.empty:
                st.warning("No overlapping in_report variants found.")
            else:
                st.success(f"Found {len(df)} overlapping in_report variant(s).")
                st.dataframe(df, use_container_width=True)

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", data=csv_bytes, file_name="results.csv", mime="text/csv")

            st.info(f"Output path: {output_path}")

        except requests.HTTPError as exc:
            st.error(f"HTTP error: {exc}")
        except Exception as exc:
            st.error(str(exc))
