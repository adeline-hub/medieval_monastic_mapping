"""
src/eda_stats.py
The Ultimate .danki Master EDA Script.
Generates 12 outputs: Classical Stats, Structural Dataviz, and UI Components.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
EDA_OUTPUT_DIR = PROJECT_ROOT / "docs" / "eda_output"
EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# .danki Brand Palette
C_BG = "#121212"
C_VERT = "#33FFA2"
C_VIOLET = "#FF33FF"
C_GREY = "#737373"
C_WHITE = "#FFFFFF"
C_CARD = "#1A1A1A"
DANKI_SCALE = [C_BG, C_GREY, C_VIOLET, C_VERT] # Custom continuous scale

def apply_danki_layout(fig, title):
    """Applies the .danki Green IT theme to Plotly figures."""
    fig.update_layout(
        title=dict(text=title, font=dict(color=C_VERT, size=18, family="Inter")),
        paper_bgcolor=C_BG, plot_bgcolor=C_BG,
        font=dict(color=C_WHITE, family="Inter, sans-serif"),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=C_GREY),
        yaxis=dict(showgrid=True, gridcolor="#222222", zeroline=False, linecolor=C_GREY),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    return fig

def main():
    print("=" * 60)
    print("DANKI INSTITUTIONAL AUDIT: MASTER EDA PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 0. LOAD & PREP DATA
    # ---------------------------------------------------------
    sites = pd.read_csv(PROCESSED_DIR / "monastic_sites.csv")
    esg = pd.read_csv(PROCESSED_DIR / "esg_metrics.csv")
    network = pd.read_csv(PROCESSED_DIR / "community_network.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders_metadata.csv")

    df = sites.merge(esg, on="name", how="inner")
    df['economic_activities'] = df.get('economic_activities', pd.Series(["Unknown"]*len(df))).fillna("Unknown")
    df['century_founded'] = (df['founded'] // 100) * 100
    top_orders = df['order'].value_counts().head(8).index

    print("\n--- PHASE 1: CLASSICAL STATISTICAL EDA ---")
    
    # =========================================================
    # EDA 1: CORRELATION MATRIX (Heatmap)
    # =========================================================
    num_cols = ['lifespan', 'environmental', 'social', 'governance', 'composite', 'lat', 'lon']
    corr_matrix = df[num_cols].corr().round(2)
    
    fig_corr = px.imshow(
        corr_matrix, text_auto=True, color_continuous_scale=DANKI_SCALE,
        title="Pearson Correlation Matrix: ESG, Lifespan & Geography"
    )
    fig_corr.update_layout(paper_bgcolor=C_BG, plot_bgcolor=C_BG, font=dict(color=C_WHITE))
    fig_corr.write_html(EDA_OUTPUT_DIR / "eda_1_correlation_matrix.html", include_plotlyjs="cdn")
    print(" [✓] eda_1_correlation_matrix.html")

    # =========================================================
    # EDA 2: SCATTER PLOT (Lifespan vs ESG with Marginal Distributions)
    # =========================================================
    fig_scatter = px.scatter(
        df[df['order'].isin(top_orders)], x='composite', y='lifespan', color='order',
        marginal_x="violin", marginal_y="violin", hover_name="name",
        title="Bivariate Analysis: ESG Composite Score vs Institutional Lifespan",
        color_discrete_sequence=[C_VERT, C_VIOLET, C_GREY, "#FFFFFF", "#AAAAAA"]
    )
    fig_scatter = apply_danki_layout(fig_scatter, "Bivariate Analysis: ESG Score vs Lifespan")
    fig_scatter.write_html(EDA_OUTPUT_DIR / "eda_2_scatter_esg_lifespan.html", include_plotlyjs="cdn")
    print(" [✓] eda_2_scatter_esg_lifespan.html")

    # =========================================================
    # EDA 3: PIVOT CHART (Order vs Century Founded Heatmap)
    # =========================================================
    pivot_df = pd.pivot_table(df[df['order'].isin(top_orders)], 
                              values='name', index='order', columns='century_founded', 
                              aggfunc='count', fill_value=0)
    fig_pivot = px.imshow(
        pivot_df, color_continuous_scale=DANKI_SCALE, text_auto=True,
        title="Pivot Chart: Volume of Foundations by Order across Centuries"
    )
    fig_pivot.update_layout(paper_bgcolor=C_BG, plot_bgcolor=C_BG, font=dict(color=C_WHITE))
    fig_pivot.write_html(EDA_OUTPUT_DIR / "eda_3_pivot_foundations.html", include_plotlyjs="cdn")
    print(" [✓] eda_3_pivot_foundations.html")

    # =========================================================
    # EDA 4: DISTRIBUTION BAR (Causes of Dissolution)
    # =========================================================
    diss_df = df['dissolution_cause'].dropna().value_counts().reset_index()
    diss_df.columns = ['Cause', 'Count']
    fig_diss = px.bar(
        diss_df.head(10), x='Count', y='Cause', orientation='h',
        title="Categorical Distribution: Top 10 Identified Causes of Dissolution",
        color_discrete_sequence=[C_VIOLET]
    )
    fig_diss.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_diss = apply_danki_layout(fig_diss, "Top Causes of Dissolution")
    fig_diss.write_html(EDA_OUTPUT_DIR / "eda_4_dissolution_causes.html", include_plotlyjs="cdn")
    print(" [✓] eda_4_dissolution_causes.html")


    print("\n--- PHASE 2: STRUCTURAL DATAVIZ (Requested) ---")

    # =========================================================
    # EDA 5: TREEMAP (Economic Ecosystem)
    # =========================================================
    tree_df = df[df['economic_activities'] != "Unknown"]
    fig_tree = px.treemap(
        tree_df, path=[px.Constant("All Economies"), 'order', 'economic_activities'],
        color='composite', color_continuous_scale=DANKI_SCALE,
        title="Economic Hierarchy: Activities by Order (Colored by ESG)"
    )
    fig_tree.update_layout(paper_bgcolor=C_BG, font=dict(color=C_WHITE))
    fig_tree.write_html(EDA_OUTPUT_DIR / "eda_5_treemap_economy.html", include_plotlyjs="cdn")
    print(" [✓] eda_5_treemap_economy.html")

    # =========================================================
    # EDA 6: TIMELINE (Lifespan by Century)
    # =========================================================
    timeline = df.groupby('century_founded')['lifespan'].mean().reset_index()
    fig_line = px.line(timeline, x="century_founded", y="lifespan", markers=True, 
                       title="Macro Trend: Average Lifespan by Century Founded")
    fig_line.update_traces(line=dict(color=C_VERT, width=3), marker=dict(color=C_VIOLET, size=8))
    fig_line = apply_danki_layout(fig_line, "Macro Trend: Average Lifespan by Century")
    fig_line.write_html(EDA_OUTPUT_DIR / "eda_6_timeline.html", include_plotlyjs="cdn")
    print(" [✓] eda_6_timeline.html")

    # =========================================================
    # EDA 7: TOP 10 LONGEVITY (Horizontal Bar)
    # =========================================================
    top_oldest = df.sort_values('lifespan', ascending=False).head(10)
    fig_bar = px.bar(
        top_oldest, x="lifespan", y="name", color="order", orientation='h',
        title="The Endurance Nodes: Top 10 Longest Surviving Communities",
        color_discrete_sequence=[C_VERT, C_VIOLET, C_GREY, "#FFFFFF"]
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_bar = apply_danki_layout(fig_bar, "Top 10 Longest Surviving Communities")
    fig_bar.write_html(EDA_OUTPUT_DIR / "eda_7_top10_bar.html", include_plotlyjs="cdn")
    print(" [✓] eda_7_top10_bar.html")

    # =========================================================
    # EDA 8 & 9: STATISTICAL TABLES (Plotly Tables)
    # =========================================================
    stats_df = df[df['order'].isin(top_orders[:5])].groupby('order').agg(
        Count=('name', 'count'), Avg_Lifespan=('lifespan', 'mean'), Avg_ESG=('composite', 'mean')
    ).round(1).reset_index().sort_values('Count', ascending=False)

    fig_tab1 = go.Figure(data=[go.Table(
        header=dict(values=["<b>Order</b>", "<b>Volume</b>", "<b>Avg Lifespan</b>", "<b>Avg ESG</b>"], fill_color=C_BG, font=dict(color=C_VERT, size=14), line_color=C_VERT),
        cells=dict(values=[stats_df.order, stats_df.Count, stats_df.Avg_Lifespan, stats_df.Avg_ESG], fill_color=C_BG, font=dict(color=C_WHITE), line_color=C_GREY)
    )])
    fig_tab1.update_layout(title="Summary Stats: Top 5 Orders", paper_bgcolor=C_BG, font=dict(family="Inter"))
    fig_tab1.write_html(EDA_OUTPUT_DIR / "eda_8_table_stats.html", include_plotlyjs="cdn")
    print(" [✓] eda_8_table_stats.html")


    print("\n--- PHASE 3: GEOSPATIAL & FRONT-END UI ---")

    # =========================================================
    # UI 10: NETWORK MAP (Updated to new Plotly 'scattermap' API)
    # =========================================================
    fig_net = go.Figure()
    for _, row in network.iterrows():
        try:
            s_node = sites[sites['name'] == row['source']].iloc[0]
            t_node = sites[sites['name'] == row['target']].iloc[0]
            fig_net.add_trace(go.Scattermap(
                lat=[s_node['lat'], t_node['lat']], lon=[s_node['lon'], t_node['lon']],
                mode='lines', line=dict(width=1, color=C_GREY), hoverinfo='none', showlegend=False
            ))
        except IndexError:
            continue
            
    fig_net.add_trace(go.Scattermap(
        lat=sites['lat'], lon=sites['lon'], mode='markers', marker=dict(size=5, color=C_VERT),
        text=sites['name'], hoverinfo='text', showlegend=False
    ))
    
    fig_net.update_layout(
        map=dict(style="carto-darkmatter", zoom=3, center=dict(lat=45, lon=15)), 
        paper_bgcolor=C_BG, 
        margin=dict(l=0, r=0, t=0, b=0)
    )
    fig_net.write_html(EDA_OUTPUT_DIR / "ui_10_network_map.html", include_plotlyjs="cdn")
    print(" [✓] ui_10_network_map.html")

    # =========================================================
    # UI 11: PODIUM (HTML Mockup)
    # =========================================================
    top3 = sites.sort_values('lifespan', ascending=False).head(3).reset_index(drop=True)
    
    # 1. FORCE EXACT MATCH: Clean strings on both sides before merging
    top3['order'] = top3['order'].astype(str).str.strip()
    orders['order'] = orders['order'].astype(str).str.strip()
    
    # 2. MERGE
    if 'Image 1' in orders.columns:
        top3 = top3.merge(orders[['order', 'Image 1']], on='order', how='left')
        
        # 3. CLEAN URLs: Extract the first clean link, ignore NaNs and messy Excel characters
        def clean_url(val):
            if pd.isna(val) or str(val).strip() == "" or str(val) == "nan":
                return f"https://via.placeholder.com/300x200/{C_BG.replace('#','')}/{C_VERT.replace('#','')}?text=No+Image"
            # Split by comma or space in case there are multiple links, and strip whitespace
            clean_link = str(val).split(',')[0].split(' ')[0].strip()
            return clean_link
            
        top3['image'] = top3['Image 1'].apply(clean_url)
    else:
        top3['image'] = f"https://via.placeholder.com/300x200/{C_BG.replace('#','')}/{C_VERT.replace('#','')}?text=Missing+Col"
    
    # Generate the HTML
    html_podium = f"""
    <html><body style="font-family:'Inter',sans-serif; background:{C_BG}; color:{C_WHITE}; padding:40px;">
        <h2>Top 3 Enduring Communities</h2>
        <div style="display:flex; gap:20px; align-items:flex-end;">
            <div style="background:{C_WHITE}; color:#000; padding:20px; border-radius:8px; width:250px; border:3px solid {C_VERT}; height:350px; text-align:center;">
                <b style="color:{C_VERT}; font-size:18px;">1st Place</b><br><br>
                <img src="{top3.loc[0,'image']}" style="width:100%; height:140px; object-fit:cover; border-radius:4px;">
                <h3 style="margin:10px 0 5px 0;">{top3.loc[0,'name']}</h3>
                <p style="margin:0; color:#555;">{top3.loc[0,'lifespan']:.0f} years</p>
                <p style="margin:0; font-size:12px; color:#888;">{top3.loc[0,'order']}</p>
            </div>
            <div style="background:{C_WHITE}; color:#000; padding:20px; border-radius:8px; width:250px; height:310px; text-align:center;">
                <b style="color:{C_GREY}; font-size:16px;">2nd Place</b><br><br>
                <img src="{top3.loc[1,'image']}" style="width:100%; height:120px; object-fit:cover; border-radius:4px;">
                <h3 style="margin:10px 0 5px 0;">{top3.loc[1,'name']}</h3>
                <p style="margin:0; color:#555;">{top3.loc[1,'lifespan']:.0f} years</p>
                <p style="margin:0; font-size:12px; color:#888;">{top3.loc[1,'order']}</p>
            </div>
            <div style="background:{C_WHITE}; color:#000; padding:20px; border-radius:8px; width:250px; height:270px; text-align:center;">
                <b style="color:{C_GREY}; font-size:16px;">3rd Place</b><br><br>
                <img src="{top3.loc[2,'image']}" style="width:100%; height:100px; object-fit:cover; border-radius:4px;">
                <h3 style="margin:10px 0 5px 0;">{top3.loc[2,'name']}</h3>
                <p style="margin:0; color:#555;">{top3.loc[2,'lifespan']:.0f} years</p>
                <p style="margin:0; font-size:12px; color:#888;">{top3.loc[2,'order']}</p>
            </div>
        </div>
    </body></html>
    """
    with open(EDA_OUTPUT_DIR / "ui_11_podium.html", "w", encoding="utf-8") as f: 
        f.write(html_podium)
    print(" [✓] ui_11_podium.html")

    print("\n" + "=" * 60)
    print("MASTER EDA COMPLETE. 11 Files output to docs/eda_output/")
    print("=" * 60)

if __name__ == "__main__":
    main()