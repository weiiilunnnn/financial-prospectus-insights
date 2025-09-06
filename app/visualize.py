# app/visualize.py
import matplotlib.pyplot as plt
import numpy as np
from models import RiskFactor
from PIL import Image, ImageDraw, ImageFont
import plotly.express as px
import pandas as pd
from models import RiskFactor, Ratios

def build_category_matrix(risks):
    # categories as rows; single column (we'll average severity)
    cats = sorted(list(set([r.category for r in risks])))
    values = []
    for c in cats:
        vals = [r.severity for r in risks if r.category == c]
        values.append(np.mean(vals) if vals else 0.0)
    return cats, np.array(values).reshape(len(values), 1)

def draw_heatmap(risks, out_path="out/risk_heatmap.png"):
    cats, matrix = build_category_matrix(risks)
    fig, ax = plt.subplots(figsize=(3, len(cats)*0.5 + 1))
    im = ax.imshow(matrix, aspect="auto", cmap="Reds", vmin=0, vmax=1)
    ax.set_xticks([])
    ax.set_yticks(np.arange(len(cats)))
    ax.set_yticklabels(cats)
    for i in range(len(cats)):
        ax.text(0, i, f"{matrix[i,0]:.2f}", va='center', ha='center', color='black')
    plt.colorbar(im, orientation='vertical', fraction=0.05)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path

def plot_ratios_bar(ratios: Ratios):
    data = {
        "Ratio": ["P/E", "P/B", "ROE (%)", "Dividend Yield (%)", "NAV"],
        "Value": [
            ratios.pe or 0,
            ratios.pb or 0,
            ratios.roe_pct or 0,
            ratios.dividend_yield_pct or 0,
            ratios.nav or 0
        ]
    }
    df = pd.DataFrame(data)
    fig = px.bar(df, x="Ratio", y="Value", text="Value",
                 title="Financial Ratios", color="Value",
                 color_continuous_scale="Blues")
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_title="Value", xaxis_title="Ratio")
    return fig

def plot_risk_distribution(risks: list[RiskFactor]):
    df = pd.DataFrame([{"Category": r.category, "Severity": r.severity} for r in risks])
    df_grouped = df.groupby("Category").mean().reset_index()
    fig = px.bar(df_grouped, x="Category", y="Severity", text="Severity",
                 title="Average Risk Severity by Category",
                 color="Severity", color_continuous_scale="Reds")
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis=dict(range=[0,1]), yaxis_title="Severity (0-1)", xaxis_title="Category")
    return fig
# Simple PDF highlight function - draws rectangles is complex; simple overlay image example omitted
