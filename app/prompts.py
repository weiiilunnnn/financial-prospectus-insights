# app/prompts.py
FEES_PROMPT = """
You are a financial extraction assistant. Given the following prospectus text, extract numeric fees.
Return JSON only with keys: management_fee_pct, trustee_fee_pct, entry_load_pct, exit_load_pct, expense_ratio_pct.
Use null for missing. Percentages should be numbers (e.g., 1.25).
Text:
\"\"\"\n{context}\n\"\"\"
"""

RISKS_PROMPT = """
You are an analyst that finds and ranks risk factors in a prospectus. From the text below, return a JSON array of up to 10 items.
Each item: {{ "title": "...", "excerpt": "...", "category": "...", "severity": <0.0-1.0>, "page": null }}
Map category from: market, liquidity, operational, geo, policy, ESG, other.
Return JSON only.
Text:
\"\"\"\n{context}\n\"\"\"
"""

RATIOS_PROMPT = """
You are a financial extraction assistant. Extract the following ratios from the prospectus text:
- pe
- pb
- roe_pct
- dividend_yield_pct
- nav

Return JSON only. Use null if missing.
Text:
\"\"\"\n{context}\n\"\"\"
"""