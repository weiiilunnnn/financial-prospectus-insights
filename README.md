# Financial Prospectus Insights

Financial Prospectus Insights is an AI-powered tool designed to automate the **extraction and analysis of financial prospectuses**, including IPO and mutual fund documents. It processes PDF files, extracts key financial ratios, evaluates associated risks, and generates executive summaries using **Large Language Models (LLMs)**.

---

## Features

- **Automated PDF Ingestion**  
  Upload prospectuses in PDF format and extract structured text.

- **Financial Ratio Extraction**  
  Extracts key ratios such as:
  - Price-to-Earnings (PE)  
  - Price-to-Book (PB)  
  - Return on Equity (ROE)  
  - Net Asset Value (NAV)  
  - Dividend Yield  
  - Management Fees, Trustee Fees, Expense Ratios, etc.

- **Risk Analysis**  
  Identifies potential risk factors and assigns severity scores.

- **Executive Summaries**  
  Generates clear and concise overviews using LLM/NLP.

- **Data Visualization**  
  Creates risk heatmaps and ratio distribution charts.

- **Report Export**  
  Exports key insights into PDF format for easy sharing.

---

## Tech Stack

- **Programming Language**: Python 3.10+  
- **AI & NLP**: OpenAI GPT or compatible free LLMs  
- **Data Processing**: Pandas, NumPy  
- **Visualization**: Matplotlib, Plotly  
- **Embedding & Search**: FAISS  
- **Interface**: Streamlit  

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/financial-prospectus-insights.git
cd financial-prospectus-insights
pip install -r requirements.txt
