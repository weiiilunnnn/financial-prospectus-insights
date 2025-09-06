from langchain_community.llms import OpenAI
from models import ProspectusSummary
from typing import Dict

llm_summary = OpenAI(model_name="gpt-4o", temperature=0)

SUMMARY_PROMPT = """
You are an analyst generating a one-page executive summary of a prospectus.
Given the following data in JSON, produce a concise summary in Markdown:

{summary_json}

Include:
- Key fees
- Top 5 risk factors with category and severity
- Financial ratios
- Key dates
- Issuer, instrument, listing info

Return only text.
"""

def generate_executive_summary(summary: ProspectusSummary) -> str:
    import json
    json_data = json.dumps(summary.model_dump(), indent=2)
    prompt = SUMMARY_PROMPT.format(summary_json=json_data)
    resp = llm_summary(prompt)
    return resp
