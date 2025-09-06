# app/app.py
import streamlit as st
from ingest import extract_text_by_page, simple_section_split
from extract import extract_summary
from visualize import draw_heatmap
from summarize import generate_executive_summary
from pathlib import Path
import tempfile
import json
from io import BytesIO
from fpdf import FPDF
import plotly.express as px
from visualize import plot_ratios_bar, plot_risk_distribution

# -----------------------
# Page Config
# -----------------------
st.set_page_config(
    page_title="Prospectus Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("📊 LLM Financial Prospectus Analyzer — MVP")

# -----------------------
# File Upload
# -----------------------
uploaded = st.file_uploader("Upload prospectus (PDF)", type=["pdf"])

if uploaded:
    # Save uploaded PDF temporarily
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tf.write(uploaded.read())
    tf.flush()
    pdf_path = tf.name

    st.info("Ingesting PDF...")
    pages = extract_text_by_page(pdf_path)
    sections = simple_section_split(pages)

    st.info("Calling LLM to extract data (requires OPENAI_API_KEY set)...")
    summary = extract_summary(sections, Path(pdf_path).name)
    exec_summary = generate_executive_summary(summary)

    st.subheader("📊 Financial Ratios")
    with st.expander("View Ratios Chart"):
        ratios_fig = plot_ratios_bar(summary.ratios)
        st.plotly_chart(ratios_fig, use_container_width=True)

    st.subheader("⚡ Risk Severity Distribution")
    with st.expander("View Risk Severity Chart"):
        risk_fig = plot_risk_distribution(summary.risks)
        st.plotly_chart(risk_fig, use_container_width=True)

    # -----------------------
    # Sidebar: Summary & Exports
    # -----------------------
    with st.sidebar:
        st.header("Summary & Exports")
        st.markdown("**Executive Summary Preview:**")
        st.text_area("Summary Preview", exec_summary, height=300)

        # Export JSON
        st.download_button(
            "💾 Export JSON",
            data=json.dumps(summary.model_dump(), indent=2),
            file_name=f"{Path(uploaded.name).stem}_summary.json",
            mime="application/json"
        )

        # Export PDF
        def export_pdf(summary_text, heatmap_path):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.multi_cell(0, 10, "Prospectus Executive Summary\n\n")
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, summary_text)
            if heatmap_path:
                pdf.image(heatmap_path, x=10, y=None, w=pdf.w - 20)
            buf = BytesIO()
            pdf.output(buf)
            buf.seek(0)
            return buf

        pdf_buf = export_pdf(exec_summary, draw_heatmap(summary.risks))
        st.download_button(
            "💾 Export PDF",
            data=pdf_buf,
            file_name=f"{Path(uploaded.name).stem}_summary.pdf",
            mime="application/pdf"
        )

    # -----------------------
    # Main Content: Fees, Risks, Heatmap
    # -----------------------
    st.subheader("📌 Key Fees")
    with st.expander("View Fees"):
        st.json(summary.fees.model_dump())

    st.subheader("⚠️ Top Risk Factors")
    with st.expander("View Top Risks"):
        for r in summary.risks[:10]:  # show up to 10 risks
            st.markdown(f"**{r.title}** — {r.category} — severity {r.severity:.2f}")
            st.write(r.excerpt[:300])  # show excerpt

    st.subheader("📈 Risk Heatmap")
    with st.expander("View Heatmap"):
        heat_path = draw_heatmap(summary.risks, out_path="out/risk_heatmap.png")
        st.image(heat_path, caption="Category severity heatmap", use_column_width=True)

    st.success("✅ Prospectus analysis complete! Use sidebar to view summary or export.")
