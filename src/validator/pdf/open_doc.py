from pymupdf import Document, open

from src.validator.pdf.validate_font import validate_font
from src.validator.pdf.validate_inpage_style import validate_inpage_stype
from src.validator.result import ValidationResult


def open_pdf(fielpath: str) -> Document:
    return open(fielpath)

def validate_pdf(doc: Document) -> ValidationResult:
    r = ValidationResult.empty()
    validate_font(doc, r)
    validate_inpage_stype(doc, r)

    return r