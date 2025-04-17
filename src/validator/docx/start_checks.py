import docx

from src.validator.docx.content_checker import extract_and_check_headings_from_docx
from src.validator.docx.format_checker import check_formatting
from src.validator.docx.page_numbering_checker import check_page_numbering
from src.validator.result import ValidationResult


def start_check_docx_file(path: str) -> ValidationResult:
    doc = docx.Document(path)
    result = ValidationResult.empty()
    check_formatting(doc, result)
    check_page_numbering(doc, result)
    # print(extract_and_check_headings_from_docx(doc))
    # print(result.errors)
    # print(result.warnings)
    return result


result = start_check_docx_file()
