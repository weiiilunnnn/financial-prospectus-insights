# app/ingest.py
import pdfplumber
from typing import List, Dict
import re

def extract_text_by_page(pdf_path: str) -> List[str]:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            txt = p.extract_text() or ""
            pages.append(txt)
    return pages

def simple_section_split(pages: List[str]) -> Dict[str, str]:
    """
    Heuristic section slicing: return a dict mapping guessed section titles to text.
    Look for headings with common keywords.
    """
    text = "\n\n".join(pages)
    # simple split points
    split_keywords = [
        "risk factors", "risks", "important risk", "fees", "charges", 
        "financial highlights", "financial information", "financial statements",
        "management fee", "expense ratio", "investment objective"
    ]
    sections = {}
    lower = text.lower()
    for kw in split_keywords:
        idx = lower.find(kw)
        if idx != -1:
            # take 2k characters around keyword as section body
            start = max(0, idx - 300)
            end = min(len(text), idx + 2000)
            sections[kw] = text[start:end]
    # fallback: put full text under 'full_text'
    sections["full_text"] = text
    return sections
