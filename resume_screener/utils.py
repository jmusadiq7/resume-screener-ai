"""
utils.py
────────
Text extraction helpers for PDF and DOCX resume files.
"""

import io
from typing import Union
import pdfplumber
import docx2txt


def extract_text_from_pdf(file_obj) -> str:
    """
    Extract plain text from an uploaded PDF file object (Streamlit UploadedFile or file-like).
    Uses pdfplumber for accurate text layer extraction.
    """
    try:
        raw = file_obj.read()
        text_parts = []
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_docx(file_obj) -> str:
    """
    Extract plain text from an uploaded DOCX file object.
    Uses docx2txt which handles tables, headers, and footers.
    """
    try:
        raw = file_obj.read()
        text = docx2txt.process(io.BytesIO(raw))
        return text or ""
    except Exception as e:
        return f"[DOCX extraction error: {e}]"