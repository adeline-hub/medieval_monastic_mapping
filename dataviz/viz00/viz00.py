"""
Challenge: #TidyTuesday 2025 week 01
Data:      Aid Worker Security Incidents
Author:    Steven Ponce (converted to Python)
Date:      2025-01-07
"""

# 0. DATA SOURCE
"""
Aid Worker Security Incidents via Makeover Monday 2024 wk 46
Link to article: https://humanitarianoutcomes.org/sites/default/files/publications/figures_at_a_glance_2024.pdf
Source: Aid Worker Security Database (https://www.aidworkersecurity.org/incidents/search)
Data Link: https://data.world/makeovermonday/2024w46-aid-worker-security-incidents
"""

# 1. LOAD PACKAGES & SETUP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up plotting parameters
plt.rcParams['figure.figsize'] = (10, 12)
plt.rcParams['figure.dpi'] = 320
plt.rcParams['savefig.dpi'] = 320

# Create directories
Path("temp_plots").mkdir(exist_ok=True)

# 2. READ IN THE DATA
aid_raw = pd.read_excel("data/Aid Worker Incidents.xlsx")

# Clean column names (equivalent to janitor::clean_names())
aid_raw.columns = aid_raw.columns.str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)

# 3. EXAMINING THE DATA
print("Dataset shape:", aid_raw.shape)
print("\nColumn info:")
print(aid_raw.info())
print("\nFirst few rows:")
print(aid_raw.head())
print("\nSummary statistics:")
print(aid_raw.describe())

# 4. TIDYDATA

# Data for both risk score and incidents
def calculate_risk_score(df):
    return df['total_killed'] * 3 + df['total_wounded'] * 2 + df['total_kidnapped']

country_analysis = (aid_raw
    .assign(risk_score=lambda df: calculate_risk_score(df))
    .groupby('country')
    .agg({
        'risk_score': 'mean',
        'country': 'size',  # count incidents
        'total_affected': 'sum'
    })
    .rename(columns={'country': 'incidents', 'risk_score': 'avg_risk'})
    .sort_values('incidents', ascending=False)
    .head(10)
    .reset_index()
)

# Vulnerability Heatmap
org_columns = ['un', 'ingo', 'icrc', 'nrcs_and_ifrc', 'nngo']
vulnerability_data = aid_raw[org_columns + ['means_of_attack']].copy()

# Melt the dataframe (equivalent to pivot_longer)
vulnerability_matrix = pd.melt(
    vulnerability_data, 
    id_vars=['means_of_attack'],
    value_vars=org_columns,
    var_name='org_type',
    value_name='count'
)

vulnerability_matrix = (vulnerability_matrix
    .groupby(['means_of_attack', 'org_type'])
    .agg({'count': 'sum'})
    .rename(columns={'count': 'total_affected'})
    .reset_index()
)

# Clean up names
org_type_mapping = {
    'un': 'UN',
    'ingo': 'INGO', 
    'icrc': 'ICRC',
    'nrcs_and_ifrc': 'NRCS/IFRC',
    'nngo': 'NNGO'
}

vulnerability_matrix['org_type'] = vulnerability_matrix['org_type'].map(org_type_mapping)
vulnerability_matrix['means_of_attack'] = vulnerability_matrix['means_of_attack'].str.title()

# 5. VISUALIZATION

# Set up color palette
colors = {
    'palette': ['#f7fbff', '#9ecae1', '#2171b5', '#084594'],
    'text': '#252525',
    'title': '#000000',
    'subtitle': '#666666',
    'caption': '#888888'
}

# Create figure with subplots
fig = plt.figure(figsize=(15, 12))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[3, 2], hspace=0.3, wspace=0.2)

# 1. Risk Score Plot
ax1 = fig.add_subplot(gs[0, 0])
country_analysis_sorted = country_analysis.sort_values('avg_risk')
bars1 = ax1.barh(country_analysis_sorted['country'], country_analysis_sorted['avg_risk'], 
                 color=colors['palette'][3])
ax1.set_title('Risk Score by Country', fontweight='bold', fontsize=14)
ax1.text(0.02, 0.98, 'Risk Score = (Deaths × 3) + (Injuries × 2) + Kidnappings', 
         transform=ax1.transAxes, fontsize=10, verticalalignment='top', 
         color=colors['text'])
ax1.set_xlabel('Risk Score')
ax1.grid(axis='x', alpha=0.3)
ax1.set_axisbelow(True)

# 2. Incidents Count Plot  
ax2 = fig.add_subplot(gs[0, 1])
bars2 = ax2.barh(country_analysis_sorted['country'], country_analysis_sorted['incidents'],
                 color=colors['palette'][1])
ax2.set_title('Number of Incidents', fontweight='bold', fontsize=14)
ax2.set_xlabel('Number of Incidents')
ax2.set_yticklabels([])  # Remove y-axis labels since they're shown in left plot
ax2.grid(axis='x', alpha=0.3)
ax2.set_axisbelow(True)

# 3. Vulnerability Heatmap
ax3 = fig.add_subplot(gs[1, :])
pivot_data = vulnerability_matrix.pivot(index='means_of_attack', columns='org_type', values='total_affected')
im = ax3.imshow(pivot_data.values, cmap='Blues', aspect='auto')

# Set ticks and labels
ax3.set_xticks(range(len(pivot_data.columns)))
ax3.set_xticklabels(pivot_data.columns, rotation=45, ha='right')
ax3.set_yticks(range(len(pivot_data.index)))
ax3.set_yticklabels(pivot_data.index)

# Add colorbar
cbar = plt.colorbar(im, ax=ax3, shrink=0.8)
cbar.set_label('Total\nAffected', rotation=0, labelpad=20)

# Add text annotations
for i in range(len(pivot_data.index)):
    for j in range(len(pivot_data.columns)):
        if not pd.isna(pivot_data.iloc[i, j]):
            text = ax3.text(j, i, int(pivot_data.iloc[i, j]), 
                          ha="center", va="center", color="white" if pivot_data.iloc[i, j] > pivot_data.values.max()/2 else "black")

ax3.set_title('Attack Impact by Organization Type and Method', fontweight='bold', fontsize=14)
ax3.text(0.5, -0.15, 'Total number of aid workers affected by each type of attack', 
         transform=ax3.transAxes, fontsize=12, ha='center', color=colors['subtitle'])
ax3.set_xlabel('Organization Type')

# Overall title and subtitle
fig.suptitle('Aid Worker Security: A Global Analysis of Risks and Incidents', 
             fontsize=20, fontweight='bold', y=0.95, color=colors['title'])
fig.text(0.5, 0.91, 'Analysis of attack patterns and their impact on humanitarian organizations worldwide',
         ha='center', fontsize=14, color=colors['subtitle'])

# Caption
caption_text = "TidyTuesday 2025 week 01 | Aid Worker Security Database via Makeover Monday"
fig.text(0.5, 0.02, caption_text, ha='center', fontsize=10, color=colors['caption'])

plt.tight_layout()
plt.subplots_adjust(top=0.88, bottom=0.08)

# Save the plot
plt.savefig('temp_plots/aid_worker_security_analysis.png', 
            dpi=320, bbox_inches='tight', facecolor='white')
plt.show()

# 6. SESSION INFO
print("\n" + "="*50)
print("SESSION INFO")
print("="*50)
print(f"Python version: {pd.__version__}")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
print(f"Matplotlib version: {plt.matplotlib.__version__}")
print(f"Seaborn version: {sns.__version__}")
