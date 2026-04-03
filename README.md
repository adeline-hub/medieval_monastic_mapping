# System Analysis of Medieval Wealth and Geopolitical Connectivity - Monastic Mapping
*medieval monastic community unveiled*

<img width='' src='https://github.com/adeline-hub/monastic.matrix/blob/main/DATAVIZ/monasticwordcloud.png?raw=true'/>


## Executive Summary

https://adeline-hub.github.io/medieval_monastic_mapping/ 

This project treats medieval monastic communities as decentralized economic nodes. By applying data engineering and ESG frameworks, we audit how different religious orders—acting as competing institutional protocols—managed capital, optimized land (e.g., polder development), and maintained resilience across fluctuating geopolitical landscapes.

## Data Engineering Pipeline

The pipeline standardizes unstructured historical records into a structured dataset for impact analysis:

<img width='' src='https://github.com/adeline-hub/monastic.matrix/blob/main/DATAVIZ/monasticwordcloud.png?raw=true'/>

## Research Pillars

* **Protocol Analysis**: Comparing "Operating Systems" (Orders) by their land-use strategies (e.g., Cistercian frontier optimization vs. Benedictine urban stabilization).
* **Geopolitical Resilience**: Evaluating the correlation between institutional governance protocols and survivability during regional fiscal/political shocks.
* **ESG Infrastructure**: Quantifying the "environmental dividend" of monastic land reclamation, focusing on hydraulic engineering and agricultural productivity.

## Technical Stack

* **Ingestion**: Python-based web scraping and LLM-assisted Named Entity Recognition (NER).
* **Normalization**: Pandas-driven data cleaning and Min-Max scaling for comparative historical metrics.
* **Analysis**: EDA focused on spatial-temporal correlation between monastic sites and trade corridors.
* **Visualization**: Plotly/Dash for interactive spatial impact assessment.
├── **Component**  	  **Technology**	      **Goal**
├── **Workbench**	      Marimo (Python)	      Transparency of method & EDA exploration.
├── **Reporting**	      Quarto (PDF/HTML)	    Professional scientific communication.
├── **Hosting**         GitHub Pages	        Unified access to both layers.

medieval-monastic-audit/
│
├── README.md                          ← Project overview + pipeline organigram
│
├── data/
│   ├── raw/                           ← Unprocessed scraped data
│   │   ├── archives_raw.json
│   │   └── cartularies_raw.csv
│   ├── processed/                     ← Cleaned, normalized datasets
│   │   ├── monastic_sites.csv
│   │   ├── orders_metadata.csv
│   │   └── esg_metrics.csv
│   └── reference/                     ← Static lookup tables
│       ├── trade_routes.geojson
│       └── order_protocols.csv
│
├── src/
│   ├── scraping.py                    ← Web scraping pipeline
│   ├── ner_extraction.py              ← AI entity extraction (NER/LLM)
│   ├── normalization.py               ← Data cleaning & scaling
│   ├── esg_scoring.py                 ← ESG dimension calculations
│   └── viz.py                         ← Shared chart functions (Plotly)
│
├── notebooks/
│   └── eda_marimo.py                  ← Marimo interactive workbench
│
├── report/
│   ├── _quarto.yml                    ← Quarto project config
│   ├── index.qmd                      ← Scientific paper (main)
│   ├── methodology.qmd                ← Section 3: Methodology
│   ├── findings.qmd                   ← Section 4: Findings
│   ├── discussion.qmd                 ← Section 5: Discussion
│   ├── references.bib                 ← Bibliography (BibTeX)
│   ├── report-style.css               ← .danki brand stylesheet
│   └── assets/
│       ├── logo.png
│       ├── favicon.ico
│       └── pipeline_diagram.png       ← Generated organigram
│
├── docs/                              ← GitHub Pages output
│   ├── index.html                     ← Workbench (Marimo export)
│   ├── report/
│   │   └── index.html                 ← Quarto HTML output
│   └── assets/
│       ├── logo.png
│       └── favicon.ico
│
├── .gitignore
├── requirements.txt
└── LICENSE

## Core Findings
...Read Full Audit [PDF]
