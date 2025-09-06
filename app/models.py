# app/models.py
from pydantic import BaseModel
from typing import List, Optional, Dict

class Fees(BaseModel):
    management_fee_pct: Optional[float] = None
    trustee_fee_pct: Optional[float] = None
    entry_load_pct: Optional[float] = None
    exit_load_pct: Optional[float] = None
    expense_ratio_pct: Optional[float] = None

class RiskFactor(BaseModel):
    title: str
    severity: float  # 0.0 - 1.0
    category: str    # e.g., market, liquidity, operational, geo, policy, ESG
    excerpt: str
    page: Optional[int] = None

class Ratios(BaseModel):
    pe: Optional[float] = None
    pb: Optional[float] = None
    roe_pct: Optional[float] = None
    dividend_yield_pct: Optional[float] = None
    nav: Optional[float] = None

class ProspectusSummary(BaseModel):
    issuer: Optional[str] = None
    instrument: Optional[str] = None
    listing_market: Optional[str] = None
    offering_size_mil: Optional[float] = None
    fees: Fees = Fees()
    ratios: Ratios = Ratios()
    risks: List[RiskFactor] = []
    key_dates: Dict[str, Optional[str]] = {}
    source_file: Optional[str] = None