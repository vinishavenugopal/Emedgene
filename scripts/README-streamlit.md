# EMG In-Report Variant Extractor

## Available modes

- **CLI script**: `extract_overlap_genes_from_reported_CNV.py`
- **Streamlit app**: `streamlit_app.py`

Both modes authenticate to Emedgene, collect variants for a case, filter `in_report` variants, intersect variant genes with the case panel genes, and write results to `output/results.csv`.

## Environment variables

Set credentials before running:

```bash
export EMG_USERNAME="your_username"
export EMG_PASSWORD="your_password"
```

## Run as CLI

From the repository root:

```bash
python scripts/extract_overlap_genes_from_reported_CNV.py EMG824233283
```

## Run as Streamlit (intranet-accessible)

From the repository root:

```bash
streamlit run scripts/streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

- `--server.address 0.0.0.0` binds to all local interfaces so the app is reachable from your intranet.
- Access locally at `http://localhost:8501`.
- Access from another machine on your network at `http://<your-host-ip>:8501`.

## Dependencies

```bash
pip install requests pandas streamlit
```

## Output

When records are found, `output/results.csv` will include:

- `EMG_Number`
- `geneListName`
- `overlapping_genes`
- `variant_details`


