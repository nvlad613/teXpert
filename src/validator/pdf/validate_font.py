from pymupdf import Document

from src.validator.result import ValidationResult, ErrCause


def __validate_font(block, page_num, r: ValidationResult):
    font_found = False
    font_sz_found = False
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            if font_found and font_sz_found:
                return
            font_name = span.get("font", "")
            font_size = span.get("size", 0)
            if (not font_found) and ("timesnewroman" not in str(font_name).lower().replace(" ", "")):
                r.add_err(
                    ErrCause.INVALID_FONT,
                    f"На странице {page_num + 1} используется шрифт {font_name}"
                )
                font_found = True
            if (not font_sz_found) and (not (12 <= font_size <= 14)):
                r.add_err(
                    ErrCause.INVALID_FONT_SIZE,
                    f"На странице {page_num + 1} размер шрифта {font_size}pt вне диапазона 12-14pt."
                )
                font_sz_found = True

def validate_font(doc: Document, r: ValidationResult):
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            __validate_font(block, page_num, r)

