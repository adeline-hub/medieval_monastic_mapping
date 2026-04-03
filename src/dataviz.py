"""
src/dataviz.py
DANKI MASTER DATAVIZ FACTORY
Generates 3 charts per report section + 1 Image Grid.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================
# SETUP & PALETTE
# ============================================
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VIZ_DIR = PROJECT_ROOT / "docs" / "eda_output"
VIZ_DIR.mkdir(parents=True, exist_ok=True)

C_BG = "#121212"
C_VERT = "#33FFA2"
C_VIOLET = "#FF33FF"
C_GREY = "#737373"
C_WHITE = "#FFFFFF"
DANKI_SCALE = [C_BG, C_GREY, C_VIOLET, C_VERT]

def apply_danki_layout(fig, title, is_polar=False, is_map=False):
    """Applies Green IT aesthetic. Handles standard, polar, and map layouts."""
    if is_polar:
        fig.update_layout(
            title=dict(text=title, font=dict(color=C_VERT, size=18, family="Inter")),
            paper_bgcolor=C_BG, font=dict(color=C_WHITE, family="Inter"),
            polar=dict(bgcolor=C_BG, angularaxis=dict(gridcolor="#333"), radialaxis=dict(gridcolor="#333")),
            margin=dict(l=40, r=40, t=80, b=40)
        )
    elif is_map:
        fig.update_layout(
            title=dict(text=title, font=dict(color=C_VERT, size=18, family="Inter")),
            paper_bgcolor=C_BG, font=dict(color=C_WHITE, family="Inter"),
            margin=dict(l=0, r=0, t=50, b=0)
        )
    else:
        fig.update_layout(
            title=dict(text=title, font=dict(color=C_VERT, size=18, family="Inter")),
            paper_bgcolor=C_BG, plot_bgcolor=C_BG, font=dict(color=C_WHITE, family="Inter"),
            xaxis=dict(showgrid=False, zeroline=False, linecolor=C_GREY),
            yaxis=dict(showgrid=True, gridcolor="#222222", zeroline=False, linecolor=C_GREY),
            margin=dict(l=40, r=40, t=80, b=40)
        )
    return fig

def main():
    print("=" * 60)
    print("DANKI REPORT DATAVIZ FACTORY")
    print("=" * 60)

    # 1. LOAD DATA
    sites = pd.read_csv(PROCESSED_DIR / "monastic_sites.csv")
    esg = pd.read_csv(PROCESSED_DIR / "esg_metrics.csv")
    econ = pd.read_csv(PROCESSED_DIR / "economic_indicators.csv")
    network = pd.read_csv(PROCESSED_DIR / "community_network.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders_metadata.csv")

    df = sites.merge(esg, on="name", how="inner")
    df['century_founded'] = (df['founded'] // 100) * 100
    top_orders = df['order'].value_counts().head(6).index

    # =========================================================
    # PART 1: ECOSYSTEM & ESG IMPACT (3 Charts)
    # =========================================================
    print("\nGenerating Part 1: Ecosystem & ESG...")
    
    # 1.1 Radar Chart: Order Profiles
    fig_1 = go.Figure()
    for o in top_orders[:3]:
        sub = df[df['order'] == o]
        fig_1.add_trace(go.Scatterpolar(
            r=[sub['environmental'].mean(), sub['social'].mean(), sub['governance'].mean(), sub['environmental'].mean()],
            theta=['Environmental', 'Social', 'Governance', 'Environmental'],
            name=o, fill='toself'
        ))
    fig_1 = apply_danki_layout(fig_1, "1.1 Average ESG Profile by Top Orders", is_polar=True)
    fig_1.write_html(VIZ_DIR / "p1_esg_radar.html")

    # 1.2 Scatter: Environmental Score vs Lifespan
    fig_2 = px.scatter(df, x="environmental", y="lifespan", color="order",
                       title="1.2 Environmental Stewardship vs Longevity", color_discrete_sequence=[C_VERT, C_VIOLET, C_GREY, "#FFF"])
    fig_2 = apply_danki_layout(fig_2, "1.2 Environmental Score vs Institutional Lifespan")
    fig_2.write_html(VIZ_DIR / "p1_env_scatter.html")

    # 1.3 Boxplot: ESG composite by Social Extraction
    fig_3 = px.box(df.dropna(subset=['social_class']), x="social_class", y="composite", color="social_class",
                   color_discrete_sequence=[C_VIOLET, C_VERT, C_GREY])
    fig_3 = apply_danki_layout(fig_3, "1.3 ESG Performance by Social Class of Founders")
    fig_3.write_html(VIZ_DIR / "p1_social_box.html")


    # =========================================================
    # PART 2: TERRITORY & GEOPOLITICS (3 Charts)
    # =========================================================
    print("Generating Part 2: Territory & Geopolitics...")

    # 2.1 Geographic Heatmap
    fig_4 = px.density_mapbox(df, lat='lat', lon='lon', z='lifespan', radius=15,
                              color_continuous_scale=DANKI_SCALE, mapbox_style="carto-darkmatter")
    fig_4 = apply_danki_layout(fig_4, "2.1 Geopolitical Density & Lifespan Hotspots", is_map=True)
    fig_4.write_html(VIZ_DIR / "p2_geo_heatmap.html")

    # 2.2 Network Sister Communities
    fig_5 = go.Figure()
    for _, row in network.sample(min(len(network), 500)).iterrows(): # Sample to keep HTML light
        try:
            s = sites[sites['name'] == row['source']].iloc[0]
            t = sites[sites['name'] == row['target']].iloc[0]
            fig_5.add_trace(go.Scattermap(lat=[s['lat'], t['lat']], lon=[s['lon'], t['lon']], mode='lines', line=dict(width=1, color=C_GREY), showlegend=False))
        except: pass
    fig_5.add_trace(go.Scattermap(lat=sites['lat'], lon=sites['lon'], mode='markers', marker=dict(size=4, color=C_VERT), showlegend=False))
    fig_5.update_layout(map=dict(style="carto-darkmatter", zoom=3, center=dict(lat=45, lon=15)))
    fig_5 = apply_danki_layout(fig_5, "2.2 Institutional Network Connectivity", is_map=True)
    fig_5.write_html(VIZ_DIR / "p2_network_map.html")

    # 2.3 Dissolution Causes (Bar)
    causes = df['dissolution_cause'].value_counts().head(8).reset_index()
    causes.columns = ['Cause', 'Count']
    fig_6 = px.bar(causes, x='Count', y='Cause', orientation='h', color_discrete_sequence=[C_VIOLET])
    fig_6.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_6 = apply_danki_layout(fig_6, "2.3 Primary Geopolitical Threats (Dissolution Causes)")
    fig_6.write_html(VIZ_DIR / "p2_dissolution_bar.html")


    # =========================================================
    # PART 3: ECONOMY & REVENUE MODELS (3 Charts)
    # =========================================================
    print("Generating Part 3: Economy...")

    # 3.1 Treemap Economic Activities
    df['economic_activities'] = df['economic_activities'].fillna('Unknown')
    tree_df = df[df['economic_activities'] != 'Unknown']
    fig_7 = px.treemap(tree_df, path=[px.Constant("Economies"), 'order', 'economic_activities'], color='composite', color_continuous_scale=DANKI_SCALE)
    fig_7 = apply_danki_layout(fig_7, "3.1 Economic Hierarchy (Colored by ESG)")
    fig_7.update_traces(marker=dict(line=dict(color=C_BG, width=2)))
    fig_7.write_html(VIZ_DIR / "p3_econ_treemap.html")

    # 3.2 Revenue Timeline Line Chart
    econ_line = econ.groupby('year')['revenue_index'].mean().reset_index()
    fig_8 = px.line(econ_line, x='year', y='revenue_index', markers=True, color_discrete_sequence=[C_VERT])
    fig_8 = apply_danki_layout(fig_8, "3.2 Macro Average Revenue Index over Time")
    fig_8.write_html(VIZ_DIR / "p3_revenue_timeline.html")

    # 3.3 Pie Chart: Revenue Sources
    pie_data = econ['primary_revenue_source'].value_counts().reset_index().head(5)
    pie_data.columns = ['Source', 'Count']
    fig_9 = px.pie(pie_data, names='Source', values='Count', color_discrete_sequence=[C_VERT, C_VIOLET, C_GREY, "#FFF", "#444"])
    fig_9 = apply_danki_layout(fig_9, "3.3 Major Revenue Sources")
    fig_9.write_html(VIZ_DIR / "p3_revenue_pie.html")


    # =========================================================
    # PART 4: DEMOGRAPHICS & GOVERNANCE (3 Charts)
    # =========================================================
    print("Generating Part 4: Demographics...")

    # 4.1 Gender Timeline (Pivot Heatmap)
    gender_pivot = pd.pivot_table(df[df['gender'].isin(['Male', 'Female', 'Double'])], 
                                  values='name', index='gender', columns='century_founded', aggfunc='count', fill_value=0)
    fig_10 = px.imshow(gender_pivot, text_auto=True, color_continuous_scale=DANKI_SCALE)
    fig_10 = apply_danki_layout(fig_10, "4.1 Gender Demographics: Foundations by Century")
    fig_10.write_html(VIZ_DIR / "p4_gender_heatmap.html")

    # 4.2 Gender vs Lifespan
    fig_11 = px.box(df[df['gender'].isin(['Male', 'Female', 'Double'])], x='gender', y='lifespan', color='gender', color_discrete_sequence=[C_VERT, C_VIOLET, C_GREY])
    fig_11 = apply_danki_layout(fig_11, "4.2 Institutional Lifespan by Gender")
    fig_11.write_html(VIZ_DIR / "p4_gender_lifespan.html")

    # 4.3 Governance Scores vs Century
    gov_time = df.groupby('century_founded')['governance'].mean().reset_index()
    fig_12 = px.bar(gov_time, x='century_founded', y='governance', color_discrete_sequence=[C_VIOLET])
    fig_12 = apply_danki_layout(fig_12, "4.3 Evolution of Average Governance Score by Century")
    fig_12.write_html(VIZ_DIR / "p4_gov_timeline.html")


     # =========================================================
    # PART 5: THE IMAGE GRID (Local Assets & Green IT CSS Fallbacks)
    # =========================================================
    print("Generating Part 5: Local Image Grid...")
    
    import os
    import random

    # 1. UPDATED PATH: Point directly to docs/img based on your screenshot
    IMG_DIR = PROJECT_ROOT / "docs" / "img"
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Scan the local directory for images
    local_images = []
    if IMG_DIR.exists():
        for file in os.listdir(IMG_DIR):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                # Create a relative path from docs/eda_output/ back up to docs/img/
                local_images.append(f"../img/{file}")

    # 3. Prepare the grid items
    grid_items = []
    
    # Use real local images if you have them
    for img_path in local_images:
        # Extract the name, remove underscores
        raw_name = Path(img_path).stem.replace("_", " ")
        # Truncate long Wikipedia filenames so they fit beautifully in the UI card
        display_name = raw_name[:35] + "..." if len(raw_name) > 35 else raw_name
        
        item_html = f"""
            <div class="grid-item">
                <img src="{img_path}" alt="{display_name}">
                <div class="caption">
                    <span class="order" title="{raw_name}">{display_name}</span>
                </div>
            </div>
        """
        grid_items.append(item_html)

    # Shuffle so the layout looks dynamic every time
    random.shuffle(grid_items)

    # 4. Fill the rest of the 9 slots with Pure CSS Placeholders (if you have less than 9 images)
    while len(grid_items) < 9:
        placeholder_html = f"""
            <div class="grid-item">
                <div class="css-placeholder">IMAGE PENDING</div>
                <div class="caption">
                    <span class="order" style="color: {C_GREY};">Archive Offline</span>
                </div>
            </div>
        """
        grid_items.append(placeholder_html)

    # 5. Build HTML Grid (Limit to exactly 9 items for a perfect 3x3 square)
    grid_html = f"""
    <html><head><style>
        body {{ font-family: 'Inter', sans-serif; background-color: {C_BG}; color: {C_WHITE}; padding: 20px; }}
        h2 {{ color: {C_VERT}; font-size: 24px; text-align: center; margin-bottom: 30px; }}
        .grid-container {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 950px; margin: 0 auto; }}
        .grid-item {{ 
            position: relative; width: 100%; aspect-ratio: 1 / 1; 
            border: 1px solid {C_GREY}; border-radius: 8px; overflow: hidden; 
            background-color: #1A1A1A; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .grid-item:hover {{ border-color: {C_VERT}; transform: translateY(-5px); box-shadow: 0 10px 20px rgba(51,255,162,0.2); z-index: 10; }}
        .grid-item img {{ width: 100%; height: 100%; object-fit: cover; filter: grayscale(30%); transition: 0.3s; }}
        .grid-item:hover img {{ filter: grayscale(0%); }}
        .css-placeholder {{
            width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
            background: radial-gradient(circle, #222222 0%, #111111 100%);
            color: #555; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;
        }}
        .caption {{
            position: absolute; bottom: 0; left: 0; right: 0;
            background: rgba(18, 18, 18, 0.9); padding: 12px; text-align: center; border-top: 2px solid {C_VIOLET};
        }}
        .caption .order {{ display: block; color: {C_VERT}; font-weight: bold; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    </style></head><body>
        <h2>Visual Heritage: Architectural Footprint</h2>
        <div class="grid-container">
            {''.join(grid_items[:9])}
        </div>
    </body></html>
    """
    with open(VIZ_DIR / "p5_image_grid.html", "w", encoding="utf-8") as f:
        f.write(grid_html)
    print(" [✓] p5_image_grid.html")
    
    print("\n" + "=" * 60)
    print("DATAVIZ FACTORY COMPLETE. 13 files saved to docs/eda_output/")
    print("=" * 60)

if __name__ == "__main__":
    main()


