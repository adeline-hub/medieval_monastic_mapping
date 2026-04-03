"""
src/diagnostic-script.py
"""

import pandas as pd
from pathlib import Path
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

df1 = pd.read_excel(RAW_DIR / "combined_d.xlsx")
print("First row sample:")
print(df1.iloc[0].to_dict())

df2 = pd.read_excel(RAW_DIR / "orders_images.xlsx")
print("\nOrders first row sample:")
print(df2.iloc[0].to_dict())