"""
src/normalization.py
Transforms raw datasets into the 5 target CSVs
for the Medieval Monastic Audit pipeline.

Column mapping based on diagnostic output from combined_d.xlsx:
  [0]  'Community'
  [1]  'Religious order'
  [2]  'Dedication'
  [3]  'Saint cleaned'
  [4]  'Date founded'
  [5]  'Date terminated'
  [6]  'Duration'
  [7]  'Threats /  Termination'
  [8]  'Country'
  [9]  'Country ISO3 RG'
  [10] 'Town'
  [11] 'Latitude'
  [12] 'Longitude'
  [13] 'Final Gender'
  [14] 'Social extraction'
  [15] 'Litigations Sentiment Score'
  [16] 'Type'
  [17] 'Source '
  [18] 'Economic Activities'
  [19] 'Comments'
  [20] 'Privileges & papal exeptions'
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================
# PATHS
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# 1. LOAD RAW DATA
# ============================================

def load_raw_data():
    communities = pd.read_excel(RAW_DIR / "combined_d.xlsx")
    orders_img = pd.read_excel(RAW_DIR / "orders_images.xlsx")
    print(f"Communities loaded: {len(communities)} rows")
    print(f"Orders loaded: {len(orders_img)} rows")
    return communities, orders_img


# ============================================
# 2. MONASTIC SITES
# ============================================

def process_monastic_sites(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize community data into monastic_sites.csv.
    Uses .astype(str) to handle mixed-type columns safely.
    """

    def safe_strip(series):
        """Convert to string and strip, preserving NaN."""
        return series.where(series.isna(), series.astype(str).str.strip())

    sites = pd.DataFrame({
        "name":               safe_strip(df["Community"]),
        "order":              safe_strip(df["Religious order"]),
        "dedication":         safe_strip(df["Dedication"]),
        "patron_saint":       safe_strip(df["Saint cleaned"]),
        "founded":            pd.to_numeric(df["Date founded"], errors="coerce"),
        "location":           safe_strip(df["Town"]),
        "country":            safe_strip(df["Country"]),
        "country_iso":        safe_strip(df["Country ISO3 RG"]),
        "lat":                pd.to_numeric(df["Latitude"], errors="coerce"),
        "lon":                pd.to_numeric(df["Longitude"], errors="coerce"),
        "gender":             safe_strip(df["Final Gender"]),
        "social_class":       safe_strip(df["Social extraction"]),
        "type":               safe_strip(df["Type"]),
        "dissolution_year":   pd.to_numeric(df["Date terminated"], errors="coerce"),
        "dissolution_cause":  safe_strip(df["Threats /  Termination"]),
        "economic_activities": safe_strip(df["Economic Activities"]),
        "privileges":         safe_strip(df["Privileges & papal exeptions"]),
        "source":             safe_strip(df["Source "]),
        "notes":              safe_strip(df["Comments"])
    })

    # Derived columns
    sites["lifespan"] = sites["dissolution_year"].fillna(2024) - sites["founded"]
    sites["status"] = np.where(sites["dissolution_year"].isna(), "Active", "Dissolved")

    # Drop rows without coordinates
    sites = sites.dropna(subset=["lat", "lon"])

    print(f"Monastic sites processed: {len(sites)} rows")
    return sites


# ============================================
# 3. ORDERS METADATA
# ============================================

def process_orders_metadata(df_orders: pd.DataFrame, df_sites: pd.DataFrame) -> pd.DataFrame:
    
    # Clean column names dynamically to remove hidden spaces (e.g., "Earliest ")
    df_orders.columns = df_orders.columns.str.strip()
    
    # Fallback in case the column is completely missing
    if "Earliest" not in df_orders.columns:
        print("Warning: 'Earliest' column not found. Filling with NaNs.")
        df_orders["Earliest"] = np.nan
        
    if "Country" not in df_orders.columns:
        df_orders["Country"] = "Unknown"

    orders_agg = df_orders.groupby("Religious order").agg(
        countries=("Country", lambda x: ", ".join(sorted(x.dropna().astype(str).unique()))),
        earliest_foundation=("Earliest", "min"),
        country_count=("Country", "nunique")
    ).reset_index()

    orders_agg.rename(columns={"Religious order": "order"}, inplace=True)

    # Clean order names to ensure a perfect match
    orders_agg["order"] = orders_agg["order"].astype(str).str.strip()
    
    # Grab the image columns if they exist
    image_cols = [c for c in df_orders.columns if "Image" in c]
    if image_cols:
        # Get the first available image per order
        images = df_orders.groupby("Religious order")[image_cols].first().reset_index()
        images.rename(columns={"Religious order": "order"}, inplace=True)
        images["order"] = images["order"].astype(str).str.strip()
        orders_agg = orders_agg.merge(images, on="order", how="left")

    # Enrich with site-level stats from the main dataset
    site_stats = df_sites.groupby("order").agg(
        community_count=("name", "count"),
        avg_lifespan=("lifespan", "mean"),
        male_count=("gender", lambda x: (x == "Male").sum()),
        female_count=("gender", lambda x: (x == "Female").sum())
    ).reset_index()

    orders = orders_agg.merge(site_stats, on="order", how="left")

    print(f"Orders metadata processed: {len(orders)} rows")
    return orders


# ============================================
# 4. ESG METRICS
# ============================================

def process_esg_metrics(df: pd.DataFrame) -> pd.DataFrame:

    def min_max_scale(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(50, index=series.index)
        return ((series - min_val) / (max_val - min_val) * 100).round(1)

    esg = pd.DataFrame({"name": df["Community"].str.strip()})

    # Environmental proxy: lifespan as land stewardship indicator
    lifespan = pd.to_numeric(
        df["Date terminated"].fillna(2024), errors="coerce"
    ) - pd.to_numeric(df["Date founded"], errors="coerce")
    esg["environmental"] = min_max_scale(lifespan.fillna(0))

    # Social proxy: gender diversity + social class
    esg["social"] = np.where(df["Final Gender"].str.strip() == "Female", 65, 45)
    esg["social"] = np.where(
        df["Social extraction"].notna(),
        esg["social"] + 10,
        esg["social"]
    )
    esg["social"] = esg["social"].clip(0, 100)

    # Governance proxy: litigation sentiment + duration
    esg["governance"] = min_max_scale(lifespan.fillna(0))
    litigation = pd.to_numeric(
        df["Litigations Sentiment Score"], errors="coerce"
    ).fillna(0)
    esg["governance"] = (esg["governance"] * 0.7 + min_max_scale(litigation) * 0.3).round(1)

    # Composite
    esg["composite"] = (
        esg["environmental"] * 0.35 +
        esg["social"] * 0.35 +
        esg["governance"] * 0.30
    ).round(1)

    esg = esg.dropna(subset=["environmental", "social", "governance"])

    print(f"ESG metrics processed: {len(esg)} rows")
    return esg


# ============================================
# 5. COMMUNITY NETWORK
# ============================================

def process_community_network(df: pd.DataFrame, radius_km: int = 150) -> pd.DataFrame:
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return R * 2 * atan2(sqrt(a), sqrt(1-a))

    sites = df[["Community", "Religious order", "Latitude", "Longitude",
                 "Date founded", "Date terminated"]].copy()
    sites.columns = ["name", "order", "lat", "lon", "founded", "terminated"]
    sites["lat"] = pd.to_numeric(sites["lat"], errors="coerce")
    sites["lon"] = pd.to_numeric(sites["lon"], errors="coerce")
    sites["founded"] = pd.to_numeric(sites["founded"], errors="coerce")
    sites["terminated"] = pd.to_numeric(sites["terminated"], errors="coerce").fillna(2024)
    sites = sites.dropna(subset=["lat", "lon", "founded"])
    sites = sites.reset_index(drop=True)

    print(f"Computing network for {len(sites)} sites (this may take a moment)...")

    links = []
    for i in range(len(sites)):
        for j in range(i + 1, len(sites)):
            if sites.loc[i, "order"] != sites.loc[j, "order"]:
                continue

            dist = haversine(
                sites.loc[i, "lat"], sites.loc[i, "lon"],
                sites.loc[j, "lat"], sites.loc[j, "lon"]
            )

            if dist <= radius_km:
                start = max(sites.loc[i, "founded"], sites.loc[j, "founded"])
                end = min(sites.loc[i, "terminated"], sites.loc[j, "terminated"])
                shared = f"{int(start)}-{int(end)}" if end > start else "None"

                links.append({
                    "source": sites.loc[i, "name"],
                    "target": sites.loc[j, "name"],
                    "order": sites.loc[i, "order"],
                    "distance_km": round(dist, 1),
                    "shared_period": shared
                })

    network = pd.DataFrame(links)
    print(f"Community network processed: {len(network)} links")
    return network


# ============================================
# 6. ECONOMIC INDICATORS
# ============================================

def process_economic_indicators(df: pd.DataFrame) -> pd.DataFrame:

    rows = []
    for _, row in df.iterrows():
        name = row["Community"]
        founded = pd.to_numeric(row["Date founded"], errors="coerce")
        terminated = pd.to_numeric(row["Date terminated"], errors="coerce")
        econ_activity = row.get("Economic Activities", "Unknown")

        if pd.isna(founded):
            continue

        end = terminated if not pd.isna(terminated) else 2024

        start_century = int(founded // 100) * 100
        end_century = int(end // 100) * 100

        for year in range(start_century, end_century + 100, 100):
            age = year - founded
            if age < 0:
                continue

            peak = (end - founded) * 0.6
            if age <= peak:
                revenue = 30 + (age / peak) * 70
            else:
                denominator = (end - founded - peak + 1)
                if denominator == 0:
                    revenue = 50
                else:
                    revenue = 100 - ((age - peak) / denominator) * 60

            rows.append({
                "name": name,
                "year": year,
                "revenue_index": round(max(0, min(100, revenue)), 1),
                "land_area": None,
                "primary_revenue_source": econ_activity
            })

    econ = pd.DataFrame(rows)
    print(f"Economic indicators processed: {len(econ)} rows")
    return econ


# ============================================
# 7. MAIN PIPELINE
# ============================================

def main():
    print("=" * 50)
    print(".danki Normalization Pipeline")
    print("=" * 50)

    # Load
    communities_raw, orders_raw = load_raw_data()

    # Process
    sites = process_monastic_sites(communities_raw)
    esg = process_esg_metrics(communities_raw)
    economic = process_economic_indicators(communities_raw)
    orders = process_orders_metadata(orders_raw, sites)
    
    # Network is slow for 1400+ sites — run last
    print("\nNetwork computation (may take 1-2 minutes)...")
    network = process_community_network(communities_raw)

    # Save
    sites.to_csv(PROCESSED_DIR / "monastic_sites.csv", index=False, encoding="utf-8")
    orders.to_csv(PROCESSED_DIR / "orders_metadata.csv", index=False, encoding="utf-8")
    esg.to_csv(PROCESSED_DIR / "esg_metrics.csv", index=False, encoding="utf-8")
    network.to_csv(PROCESSED_DIR / "community_network.csv", index=False, encoding="utf-8")
    economic.to_csv(PROCESSED_DIR / "economic_indicators.csv", index=False, encoding="utf-8")

    print("\n" + "=" * 50)
    print("All datasets saved to data/processed/")
    print("=" * 50)


if __name__ == "__main__":
    main()