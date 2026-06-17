# 02_basic_analysis
# Reads the latest OpenFDA snapshot and performs simple exploratory analysis.


import pandas as pd
import glob
import os


# Find the latest snapshot
files = sorted(glob.glob("../data/live_snapshot_*.csv"))
if not files:
    raise FileNotFoundError("No snapshot files found in ../data/")
latest = files[-1]
print("Using snapshot:", latest)


df = pd.read_csv(latest)
print("Rows:", len(df))
print(df.head())


# Basic counts
print("\nTop drugs:")
print(df['drug'].value_counts().head())

print("\nTop reactions:")
print(df['reactions'].value_counts().head())


# Simple pivot: drug vs reaction count
pivot = df.pivot_table(index='drug', values='report_id', aggfunc='count').sort_values('report_id', ascending=False)
print("\nReports per drug:")
print(pivot.head())


