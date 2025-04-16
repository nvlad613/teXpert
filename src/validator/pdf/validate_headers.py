import re

from pymupdf import Document

from src.validator.result import ValidationResult, ErrCause

_REQUIRED_HEADINGS = [
    "СОДЕРЖАНИЕ",
    "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
    "ВВЕДЕНИЕ",
    "ЗАКЛЮЧЕНИЕ",
    "СПИСОК ИСПОЛЬЗУЕМЫХ ИСТОЧНИКОВ"
]

def __extract_page_header(s: str) -> str:
    m = re.search(r"'text'\s*:\s*'([^']+)'", s)
    if not m:
        return ""

    return m.group(1).strip()

def validate_headings_order(doc: Document, r: ValidationResult):
    """
    Проверяет, что на страницах, где размещены требуемые заголовки, каждый заголовок является первым элементом,
    а сами требуемые заголовки следуют в заданной последовательности (при игнорировании прочих заголовков).
      1. "СОДЕРЖАНИЕ"
      2. "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ"
      3. "ВВЕДЕНИЕ"
      4. "ЗАКЛЮЧЕНИЕ"
      5. "СПИСОК ИСПОЛЬЗУЕМЫХ ИСТОЧНИКОВ"
    """
    current_heading_i = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_dict = page.get_text("dict")
        # Найдём текстовый блок с минимальным y (самый верхний блок) на странице
        top_block = None
        for block in text_dict.get("blocks", []):
            if block["type"] != 0:
                continue
            if top_block is None or block["bbox"][1] < top_block["bbox"][1]:
                top_block = block
        if top_block is not None:
            heading_text = __extract_page_header(str(top_block))
            # Если заголовок совпадает - запоминаем
            if heading_text == _REQUIRED_HEADINGS[current_heading_i]:
                current_heading_i += 1
            elif heading_text in _REQUIRED_HEADINGS:
                r.add_err(ErrCause.INVALID_SECTIONS_ORDER, f"секция '{heading_text}' расположена некорректно")
                return

    if current_heading_i + 1 < len(_REQUIRED_HEADINGS):
        r.add_err(ErrCause.INVALID_SECTIONS_ORDER, "не все необходимые секции включены в документ")