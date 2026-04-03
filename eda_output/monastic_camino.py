import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ==========================================
# 1. MOCK DATA (Levant/East Africa to Europe)
# ==========================================
nodes_data = {
    'id': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'],
    'name': ['St. Anthony (Egypt)', 'Qozhaya (Lebanon)', 'Monte Cassino (Italy)', 
             'Cluny (France)', 'Citeaux (France)', 'Fountains (UK)', 'Lindisfarne (UK)'],
    'lat': [28.924, 34.283, 41.490, 46.434, 47.128, 54.109, 55.679],
    'lon': [32.349, 35.950, 13.813, 4.659, 5.066, -1.582, -1.799],
    'founded': [356, 400, 529, 910, 1098, 1132, 634],
    'lifespan': [1660, 1620, 1490, 880, 700, 400, 900],
    'order': ['Other', 'Other', 'Benedictine', 'Benedictine', 'Cistercian', 'Cistercian', 'Other']
}
df_nodes = pd.DataFrame(nodes_data)

edges_data = {
    'source': ['A1', 'A2', 'A1', 'A3', 'A4', 'A3', 'A5'],
    'target': ['A2', 'A3', 'A3', 'A4', 'A5', 'A7', 'A6'],
    'shared_period': [1200, 1100, 1100, 800, 600, 700, 400]
}
df_edges = pd.DataFrame(edges_data)

# ==========================================
# 2. BRAND PALETTE
# ==========================================
BG_COLOR = "#121212"
COLOR_MAP = {
    'Cistercian': '#33FFA2', # Fluorescent Green
    'Benedictine': '#FF33FF', # Fluorescent Violet
    'Other': '#737373'       # Grey
}

# ==========================================
# 3. ORGANIC CURVE GENERATOR (Data Humanism)
# ==========================================
def generate_bezier_curve(p0, p2, bend_factor=0.2, num_points=30):
    """Generates an organic sweeping arc between two lon/lat points."""
    # Midpoint
    mid_x = (p0[0] + p2[0]) / 2
    mid_y = (p0[1] + p2[1]) / 2
    
    # Distance and perpendicular offset for the curve
    dx = p2[0] - p0[0]
    dy = p2[1] - p0[1]
    
    # Control point (p1)
    ctrl_x = mid_x - dy * bend_factor
    ctrl_y = mid_y + dx * bend_factor

    # Quadratic Bezier formula
    t = np.linspace(0, 1, num_points)
    curve_x = (1-t)**2 * p0[0] + 2*(1-t)*t * ctrl_x + t**2 * p2[0]
    curve_y = (1-t)**2 * p0[1] + 2*(1-t)*t * ctrl_y + t**2 * p2[1]
    
    return curve_x, curve_y

fig = go.Figure()

# ==========================================
# 4. DRAWING THE CAMINO (EDGES)
# ==========================================
for _, edge in df_edges.iterrows():
    src = df_nodes[df_nodes['id'] == edge['source']].iloc[0]
    tgt = df_nodes[df_nodes['id'] == edge['target']].iloc[0]
    
    # Create the sweeping curve
    curve_x, curve_y = generate_bezier_curve((src['lon'], src['lat']), (tgt['lon'], tgt['lat']))
    
    # Opacity based on shared lifespan (normalized roughly between 0.1 and 0.6)
    opacity = max(0.15, min(0.6, edge['shared_period'] / 1500))
    
    fig.add_trace(go.Scatter(
        x=curve_x, y=curve_y,
        mode='lines',
        line=dict(color=f'rgba(115, 115, 115, {opacity})', width=1.5),
        hoverinfo='none',
        showlegend=False
    ))

# ==========================================
# 5. DRAWING THE CONSTELLATION (NODES)
# ==========================================
for order, color in COLOR_MAP.items():
    subset = df_nodes[df_nodes['order'] == order]
    
    # Node sizes scaled organically by lifespan
    sizes = np.sqrt(subset['lifespan']) * 0.8
    
    # Poetic Hover Text
    hover_text = (
        "<b>" + subset['name'] + "</b><br>" +
        "Founded: " + subset['founded'].astype(str) + " AD<br>" +
        "Lifespan: " + subset['lifespan'].astype(str) + " years<br>" +
        "Order: " + subset['order']
    )

    fig.add_trace(go.Scatter(
        x=subset['lon'], y=subset['lat'],
        mode='markers',
        name=order,
        text=hover_text,
        hoverinfo='text',
        marker=dict(
            size=sizes,
            color=color,
            opacity=0.9,
            line=dict(color=BG_COLOR, width=1.5) # Slight dark border for separation
        )
    ))

# ==========================================
# 6. LAYOUT & GREEN IT EXPORT
# ==========================================
fig.update_layout(
    plot_bgcolor=BG_COLOR,
    paper_bgcolor=BG_COLOR,
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(
        showgrid=False, zeroline=False, visible=False,
        scaleanchor="x", scaleratio=1.2 # Maintains roughly accurate geographical aspect ratio
    ),
    legend=dict(
        font=dict(color="#737373", family="Georgia, serif"),
        orientation="h",
        yanchor="bottom", y=0.02, xanchor="center", x=0.5
    ),
    hoverlabel=dict(
        bgcolor=BG_COLOR,
        font=dict(color="#33FFA2", family="Georgia, serif"),
        bordercolor="#737373"
    )
)

# Export as a lightweight HTML component. 
# include_plotlyjs='cdn' ensures the file is tiny (~10kb) by offloading JS to the browser cache.
fig.write_html("monastic_camino.html", full_html=False, include_plotlyjs='cdn')
print("Saved purely organic constellation map to monastic_camino.html")