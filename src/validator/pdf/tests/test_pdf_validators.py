import pymupdf

from src.validator.pdf.validate_font import validate_font
from src.validator.pdf.validate_headers import validate_headings_order, REQUIRED_HEADINGS
from src.validator.result import ValidationResult, ErrCause


def test_validate_font_valid():
    doc = pymupdf.open()
    page = doc.new_page()
    # Используем официальное имя шрифта из PyMuPDF
    page.insert_text(
        point=(100, 100),
        text="Valid text",
        fontname="Times-Roman",
        fontsize=12
    )
    result = ValidationResult.empty()
    validate_font(doc, result)
    assert not result.errors, f"Ошибки: {result.errors}"

def test_validate_font_invalid():
    doc = pymupdf.open()
    page = doc.new_page()
    # Используем шрифт, который точно есть в системе
    page.insert_text(
        point=(100, 100),
        text="Invalid text",
        fontname="Courier",
        fontsize=11
    )
    result = ValidationResult.empty()
    validate_font(doc, result)
    assert ErrCause.INVALID_FONT in result.errors
    assert ErrCause.INVALID_FONT_SIZE in result.errors


def test_validate_headings_correct_order(monkeypatch):
    # Сохраняем оригинальные значения
    original_headings = REQUIRED_HEADINGS.copy()

    try:
        # Временная замена на цифры
        monkeypatch.setattr(
            "src.validator.pdf.validate_headers.REQUIRED_HEADINGS",
            ["1", "2", "3", "4", "5"]
        )

        # Создаем тестовый документ
        doc = pymupdf.open()
        for heading in ["1", "2", "3", "4", "5"]:
            page = doc.new_page()
            page.insert_text((100, 50), heading, fontsize=14)

        # Выполняем проверку
        result = ValidationResult.empty()
        validate_headings_order(doc, result)

        assert not result.errors

    finally:
        # Возвращаем оригинальные значения даже при ошибках
        monkeypatch.setattr(
            "src.validator.pdf.validate_headers.REQUIRED_HEADINGS",
            original_headings
        )
