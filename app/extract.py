# app/extract.py
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import ValidationError
import json
from typing import Dict, List
from models import ProspectusSummary, Fees, RiskFactor, Ratios
from prompts import FEES_PROMPT, RISKS_PROMPT, RATIOS_PROMPT
from chunk import detect_headers_footers, clean_text_auto, chunk_text

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# ------------------------
# Helper: LLM JSON Extraction
# ------------------------
def _llm_json(prompt: str) -> dict:
    resp = llm([HumanMessage(content=prompt)])
    text_resp = resp.content
    try:
        return json.loads(text_resp)
    except Exception:
        # fallback: extract first JSON block
        import re
        m = re.search(r"(\{[\s\S]*\})", text_resp)
        if m:
            return json.loads(m.group(1))
        return {}

# ------------------------
# Extract Fees
# ------------------------
def extract_fees_from_pages(pages: List[str]) -> Fees:
    headers_footers = detect_headers_footers(pages)
    cleaned_pages = [clean_text_auto(p, headers_footers) for p in pages]
    chunks = chunk_text(cleaned_pages, max_chars=4000, overlap=200)
    
    # combine chunk text for fees extraction
    combined_text = " ".join([c['text'] for c in chunks])
    prompt = FEES_PROMPT.format(context=combined_text)
    j = _llm_json(prompt)
    
    try:
        return Fees(**j)
    except ValidationError:
        return Fees(
            management_fee_pct=j.get("management_fee_pct"),
            trustee_fee_pct=j.get("trustee_fee_pct"),
            entry_load_pct=j.get("entry_load_pct"),
            exit_load_pct=j.get("exit_load_pct"),
            expense_ratio_pct=j.get("expense_ratio_pct"),
        )

# ------------------------
# Extract Risks
# ------------------------
def extract_risks_from_pages(pages: List[str]) -> List[RiskFactor]:
    headers_footers = detect_headers_footers(pages)
    cleaned_pages = [clean_text_auto(p, headers_footers) for p in pages]
    chunks = chunk_text(cleaned_pages, max_chars=8000, overlap=400)
    
    combined_text = " ".join([c['text'] for c in chunks])
    prompt = RISKS_PROMPT.format(context=combined_text)
    arr = _llm_json(prompt) if isinstance(_llm_json(prompt), list) else []

    risks = []
    for item in arr:
        try:
            rf = RiskFactor(
                title=item.get("title", "").strip()[:200],
                excerpt=item.get("excerpt", "").strip()[:1000],
                category=item.get("category", "other"),
                severity=float(item.get("severity", 0.0)),
                page=item.get("page")
            )
            risks.append(rf)
        except Exception:
            continue
    return risks

# ------------------------
# Extract Ratios
# ------------------------
def extract_ratios_from_pages(pages: List[str]) -> Ratios:
    headers_footers = detect_headers_footers(pages)
    cleaned_pages = [clean_text_auto(p, headers_footers) for p in pages]
    chunks = chunk_text(cleaned_pages, max_chars=4000, overlap=200)
    
    combined_text = " ".join([c['text'] for c in chunks])
    prompt = RATIOS_PROMPT.format(context=combined_text)
    j = _llm_json(prompt)
    
    try:
        return Ratios(**j)
    except ValidationError:
        return Ratios(
            pe=j.get("pe"),
            pb=j.get("pb"),
            roe_pct=j.get("roe_pct"),
            dividend_yield_pct=j.get("dividend_yield_pct"),
            nav=j.get("nav")
        )

# ------------------------
# Build Prospectus Summary
# ------------------------
def extract_summary(pages: List[str], source_file: str) -> ProspectusSummary:
    fees = extract_fees_from_pages(pages)
    risks = extract_risks_from_pages(pages)
    ratios = extract_ratios_from_pages(pages)

    summary = ProspectusSummary(
        issuer=None,
        instrument=None,
        listing_market=None,
        offering_size_mil=None,
        fees=fees,
        ratios=ratios,
        risks=risks,
        key_dates={},
        source_file=source_file
    )
    return summary
