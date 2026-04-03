"""
src/data_quality.py
Quick audit of raw data before normalization.
"""

import pandas as pd
from pathlib import Path

# Go UP one level from src/ to archives/, then into data/raw/
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

print(f"Project root: {PROJECT_ROOT}")
print(f"Raw data dir: {RAW_DIR}")
print(f"Files found: {list(RAW_DIR.glob('*.xlsx'))}")


def audit_raw_data(filepath: Path):
    print(f"\nLooking for file at: {filepath}")
    
    df = pd.read_excel(filepath)
    
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nSample:\n{df.head(3)}")
    
    # Check coordinates
    lat = pd.to_numeric(df.get("Latitude"), errors="coerce")
    lon = pd.to_numeric(df.get("Longitude"), errors="coerce")
    print(f"\nCoordinates: {lat.notna().sum()}/{len(df)} valid")
    
    # Check orders
    if "Religious order" in df.columns:
        print(f"\nUnique orders: {df['Religious order'].nunique()}")
        print(df["Religious order"].value_counts().head(10))


if __name__ == "__main__":
    audit_raw_data(RAW_DIR / "combined_d.xlsx")