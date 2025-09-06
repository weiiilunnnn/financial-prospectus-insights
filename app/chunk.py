# app/chunk.py
import re
from collections import Counter
from typing import List, Dict, Tuple
import bisect

# ------------------------
# Header/Footer Detection
# ------------------------
def detect_headers_footers(pages: List[str], sample_size: int = 10) -> List[str]:
    """
    Detect repeated headers/footers by sampling the first and last N pages.
    Returns a list of repeated phrases to remove.
    """
    sample_texts = pages[:sample_size] + pages[-sample_size:]
    line_counts = Counter()

    for page in sample_texts:
        lines = [l.strip() for l in page.split("\n") if l.strip()]
        for line in lines:
            if 3 < len(line) < 80:  # avoid tiny numbers or full paragraphs
                line_counts[line] += 1

    threshold = max(3, len(sample_texts) // 2)  # appears in at least half of sample pages
    repeated_lines = [line for line, count in line_counts.items() if count >= threshold]
    return repeated_lines

# ------------------------
# Cleaning Function
# ------------------------
def clean_text_auto(raw_text: str, headers_footers: List[str]) -> str:
    """
    Clean text by removing headers/footers, page numbers, artifacts, and fix line breaks.
    """
    text = raw_text

    # Remove (cid:...) artifacts
    text = re.sub(r'\(cid:\d+\)', '', text)

    # Remove page numbers like "Page 1 of 10" or standalone digits
    text = re.sub(r'Page\s*\d+\s*(of\s*\d+)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Remove detected headers/footers
    for hf in headers_footers:
        pattern = re.escape(hf)
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Fix broken lines and extra spaces
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()

# ------------------------
# Sentence Splitting
# ------------------------
def _split_sentences(text: str) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[\.\?\!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# ------------------------
# Split Long Sentence
# ------------------------
def _split_long_sentence(sentence: str, max_chars: int, overlap: int) -> List[str]:
    words = sentence.split()
    chunks = []
    start = 0
    while start < len(words):
        curr = []
        length = 0
        i = start
        while i < len(words) and length + len(words[i]) + 1 <= max_chars:
            curr.append(words[i])
            length += len(words[i]) + 1
            i += 1
        if not curr:
            # single word longer than max_chars, force split
            w = words[start]
            chunks.append(w[:max_chars])
            words[start] = w[max_chars:]
            continue
        chunks.append(" ".join(curr))
        overlap_words = max(1, overlap // 6)
        start = max(start + len(curr) - overlap_words, start + 1)
    return chunks

# ------------------------
# Page Offset Helpers
# ------------------------
def _char_offsets_for_pages(pages: List[str], sep: str = "\n\n") -> Tuple[str, List[int]]:
    offsets = []
    curr = 0
    for p in pages:
        offsets.append(curr)
        curr += len(p) + len(sep)
    combined_text = sep.join(pages)
    return combined_text, offsets

def _page_for_char(offsets: List[int], char_index: int) -> int:
    idx = bisect.bisect_right(offsets, char_index) - 1
    return max(0, idx)

# ------------------------
# Chunking Function
# ------------------------
def chunk_text(
    pages: List[str],
    max_chars: int = 1000,
    overlap: int = 200,
    sep: str = "\n\n"
) -> List[Dict]:
    """
    Chunk cleaned text into manageable pieces for extraction.
    Returns list of dicts with metadata: chunk_id, text, start_char, end_char, start_page, end_page
    """
    if not pages:
        return []

    combined_text, offsets = _char_offsets_for_pages(pages, sep=sep)
    sentences = _split_sentences(combined_text)

    chunks = []
    buffer = ""
    buffer_start_char = 0
    running_index = 0

    for sent in sentences:
        sent_start = combined_text.find(sent, running_index)
        sent_start = sent_start if sent_start != -1 else running_index
        sent_end = sent_start + len(sent)
        running_index = sent_end

        if len(buffer) + len(sent) + 1 <= max_chars:
            if not buffer:
                buffer = sent
                buffer_start_char = sent_start
            else:
                buffer += " " + sent
        else:
            # flush buffer as a chunk
            if buffer:
                chunk_start = buffer_start_char
                chunk_end = buffer_start_char + len(buffer)
                chunks.append({
                    "chunk_id": len(chunks) + 1,
                    "text": buffer.strip(),
                    "start_char": chunk_start,
                    "end_char": chunk_end,
                    "start_page": _page_for_char(offsets, chunk_start),
                    "end_page": _page_for_char(offsets, chunk_end)
                })
            # start new buffer with overlap
            overlap_text = buffer[-overlap:] if buffer else ""
            new_buf = (overlap_text + " " + sent).strip()
            if len(new_buf) > max_chars:
                long_chunks = _split_long_sentence(sent, max_chars=max_chars, overlap=overlap)
                for lc in long_chunks:
                    lc_start = combined_text.find(lc, running_index - len(sent))
                    lc_start = lc_start if lc_start != -1 else running_index
                    lc_end = lc_start + len(lc)
                    chunks.append({
                        "chunk_id": len(chunks) + 1,
                        "text": lc.strip(),
                        "start_char": lc_start,
                        "end_char": lc_end,
                        "start_page": _page_for_char(offsets, lc_start),
                        "end_page": _page_for_char(offsets, lc_end)
                    })
                buffer = ""
                buffer_start_char = running_index
            else:
                buffer = new_buf
                buffer_start_char = sent_start - len(overlap_text)

    # flush remaining buffer
    if buffer:
        chunk_start = buffer_start_char
        chunk_end = buffer_start_char + len(buffer)
        chunks.append({
            "chunk_id": len(chunks) + 1,
            "text": buffer.strip(),
            "start_char": chunk_start,
            "end_char": chunk_end,
            "start_page": _page_for_char(offsets, chunk_start),
            "end_page": _page_for_char(offsets, chunk_end)
        })

    return chunks
