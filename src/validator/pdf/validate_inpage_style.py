import re

from pymupdf import Document

from src.validator.result import ValidationResult, ErrCause

_TOL = 30


def __extract_page_number(s: str) -> int:
    m = re.search(r"'text'\s*:\s*'([^']+)'", s)
    if not m:
        return 0

    val = m.group(1).strip()
    try:
        if re.fullmatch(r'[+-]?\d+', val):
            return int(val)
    except ValueError:
        return 0
    return 0

def validate_inpage_stype(doc: Document, r: ValidationResult):
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_rect = page.rect
        # Для листа A4 размеры примерно 210x297 мм. Перевод в поинты (1 мм ≈ 2.83465 pt)
        # Левое поле: 30мм -> ~85pt, правое: 10-15мм (~28pt-42pt), верхнее и нижнее: 20мм (~57pt)
        left_bound = 85
        right_bound = page_rect.width - 42
        top_bound = 57
        bottom_bound = page_rect.height - 57

        mid_x = page_rect.width / 2
        bottom_y = page_rect.height

        text_dict = page.get_text("dict")
        numbering_found = False

        for block in text_dict["blocks"]:
            if block["type"] != 0:
                continue
            bbox = block["bbox"]  # [x0, y0, x1, y1]

            # проверяем поля
            if (block.get("text") and len(block["text"] > 150)) and (not r.has_err(ErrCause.INVALID_PAGE_FIELDS)):
                if bbox[0] < left_bound or bbox[2] > right_bound or bbox[1] < top_bound or bbox[3] > bottom_bound:
                    r.add_err(ErrCause.INVALID_PAGE_FIELDS, f"некорректные поля на странице {page_num}")

            # проверяем нумерацию
            if abs(bbox[3] - bottom_y) < 50:
                page_n = __extract_page_number(str(block))
                if page_n > 0:
                    block_mid_x = (bbox[0] + bbox[2]) / 2
                    if abs(block_mid_x - mid_x) < _TOL and page_n == page_num + 1:
                        numbering_found = True
                        break

        if not numbering_found:
            r.add_err(ErrCause.INVALID_PAGE_NUMBERING, "некорректная нумерация страниц")
        if r.has_err(ErrCause.INVALID_PAGE_NUMBERING) and r.has_err(ErrCause.INVALID_PAGE_FIELDS):
            return
