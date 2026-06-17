import pandas as pd
import glob
import os
from datetime import datetime

def load_latest_snapshot():
    files = sorted(glob.glob("../data/live_snapshot_*.csv"))
    if not files:
        raise FileNotFoundError("No snapshot files found in ../data/")
    return files[-1]

def generate_html(df, snapshot_name):
    html = f"""
    <html>
    <head>
        <title>Pharmacovigilance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            table {{ border-collapse: collapse; width: 80%; margin-bottom: 30px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Pharmacovigilance Report</h1>
        <p><strong>Snapshot used:</strong> {snapshot_name}</p>
        <p><strong>Generated:</strong> {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")}</p>

        <h2>Top Drugs</h2>
        {df['drug'].value_counts().head().to_frame().to_html()}

        <h2>Top Reactions</h2>
        {df['reactions'].value_counts().head().to_frame().to_html()}

        <h2>Reports per Drug</h2>
        {df.pivot_table(index='drug', values='report_id', aggfunc='count').sort_values('report_id', ascending=False).head().to_html()}
    </body>
    </html>
    """
    return html

def main():
    snapshot = load_latest_snapshot()
    df = pd.read_csv(snapshot)

    html = generate_html(df, snapshot_name=os.path.basename(snapshot))

    os.makedirs(".", exist_ok=True)
    out_path = "../docs/latest_report.html"
    with open(out_path, "w") as f:
        f.write(html)

    print("Generated:", out_path)

if __name__ == "__main__":
    main()
