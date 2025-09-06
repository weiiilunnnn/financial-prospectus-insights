# app/risk.py
from typing import List
from models import RiskFactor
import math
import re

RISK_KEYLEX = {
    "market": ["market", "price", "volatility", "equity market", "share price"],
    "liquidity": ["liquid", "liquidity", "marketability", "redemption", "illiquid"],
    "operational": ["operational", "systems", "process", "fraud", "counterparty", "service interruption"],
    "geo": ["country", "political", "geopolitical", "sanction", "jurisdiction"],
    "policy": ["regulat", "tax", "policy", "legislation", "compliance"],
    "ESG": ["environment", "carbon", "sustainab", "social", "governance"]
}

def keyword_severity(excerpt: str) -> float:
    s = excerpt.lower()
    score = 0.0
    for cat, kw_list in RISK_KEYLEX.items():
        for kw in kw_list:
            if kw in s:
                score += 0.2
    # hedging adjustment
    if re.search(r"\b(may|might|could|possible|potential)\b", s):
        score *= 0.8
    return max(0.0, min(1.0, score))

def normalize_risks(risks: List[RiskFactor]) -> List[RiskFactor]:
    normalized = []
    for r in risks:
        auto = keyword_severity(r.excerpt)
        # final severity average of LLM-provided and heuristic
        if r.severity is None:
            final = auto
        else:
            final = (float(r.severity) + auto) / 2.0
        r.severity = max(0.0, min(1.0, final))
        normalized.append(r)
    return normalized
