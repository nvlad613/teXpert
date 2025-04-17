import docx
from typing import Dict, List
from docx.oxml.text.run import CT_R
from docx.oxml.ns import qn

from docx import Document
from docx.oxml.ns import qn

from src.validator.result import ValidationResult, ErrCause


def part_has_page_field(part) -> bool:
    """
    Проверяем, встречается ли PAGE в любом <w:fldSimple w:instr="…">
    или <w:instrText> в данном header/footer.
    """
    if part is None:
        return False
    xml = part._element.xml           # сырой XML колонтитула
    return ' PAGE ' in xml.upper()    # минимальная, но надёжная проверка

def section_has_page(section) -> bool:
    """Проверяем ВСЕ разновидности колонтитулов секции."""
    return any(
        part_has_page_field(p) for p in (
            section.footer, section.header,
            section.first_page_footer, section.first_page_header,
            section.even_page_footer,  section.even_page_header
        )
    )

def check_page_numbering(doc: docx.Document(), result: ValidationResult):
    missing = [str(i) for i, sec in enumerate(doc.sections, 1)
               if not section_has_page(sec)]
    if missing:
        result.add_err(ErrCause.INVALID_PAGE_NUMBERING, "numbering doesn't exist")
