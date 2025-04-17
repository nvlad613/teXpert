from typing import Dict, Any
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as WDAP
import docx
import re

from src.validator.result import ValidationResult, ErrCause


def get_effective_fontname(doc: docx.Document, para: docx.text.paragraph.Paragraph, run: docx.text.run.Run) -> str:
    # 1. Если в самом run.font явно указан шрифт
    if run.font and run.font.name:
        return run.font.name

    # 2. Если у run есть стиль (run.style) и там прописан шрифт
    if run.style and run.style.font and run.style.font.name:
        return run.style.font.name

    # 3. Смотрим стиль абзаца
    para_style = para.style
    if para_style and para_style.font and para_style.font.name:
        return para_style.font.name

    # 4. Поднимаемся по base_style
    style_candidate = para_style
    while style_candidate and style_candidate.base_style:
        base = style_candidate.base_style
        if base.font and base.font.name:
            return base.font.name
        style_candidate = base

    # 5. Проверяем стиль 'Normal' (часто основной)
    if 'Normal' in doc.styles:
        normal_style = doc.styles['Normal']
        if normal_style and normal_style.font and normal_style.font.name:
            return normal_style.font.name

    return None


def doc_contains_only_tnr(doc: docx.Document()) -> bool:
    for para in doc.paragraphs:
        for run in para.runs:
            eff_font = get_effective_fontname(doc, para, run)
            if eff_font is None:
                # Если вы хотите допустить, что None = Times New Roman, закомментируйте эту строку:
                continue

            # Здесь проверяем, что строка eff_font действительно содержит "Times New Roman"
            # с учётом возможных вариаций ("Times New Roman CE", "Times New Roman Bold" и т.п.).
            if not re.search(r'times\s*new\s*roman', eff_font, re.IGNORECASE):
                return False
    return True


def check_formatting(doc: docx.Document, result: ValidationResult) -> Dict[str, Any]:
    """
    Проверка форматирования (Times New Roman, размер шрифта 12–14, чёрный цвет и т. п.)
    в .docx-файле. Для .doc нужно сначала конвертировать в docx.

    Ограничения:
     - python-docx не всегда возвращает точное название шрифта (может не передаваться)
     - Межстрочный интервал, выравнивание, поля страницы также читаются ограниченно.

    Пример наброска: смотрим каждый параграф,
    у каждого run проверяем font.name, font.size, font.color
    """
    results = {
        "font_check": True,
        "font_size_check": True,
        "color_check": True,
        "line_spacing_check": True,  # в python-docx проверка немного сложнее
        "alignment_check": True,  # то же самое
        "page_margins_check": True,  # margins в docx можно смотреть через section
    }
    BLACK = RGBColor(0x00, 0x00, 0x00)
    # Пример: проверка первого секционного размета на поля
    section = doc.sections[0]
    # Ширина левого поля (section.left_margin) хранится в EMU (English Metric Units)
    # 1 дюйм = 914400 EMU, 1 см = 360000 EMU
    # Нужно переводить EMU в мм.
    # Для проверки «левое поле = 30 мм»:
    left_margin_mm = section.left_margin / 36000.0
    # Допустим, если оно сильно отклоняется от 30, считаем ошибкой
    if not (29.5 <= left_margin_mm <= 30.5):
        result.add_err(ErrCause.INVALID_PAGE_FIELDS, "left margin must be between 29.5 and 30.5")
        results["page_margins_check"] = False

    # Перебираем параграфы и их 'run'
    for para in doc.paragraphs:
        for run in para.runs:
            font = run.font
            # Пример проверки шрифта:
            # 1) font.name может быть None (если он наследуется от стиля),
            #    тогда надо смотреть стиль параграфа и т.д.
            # 2) В реальности проверять + "Times New Roman CYR" и другие вариации
            if font.name and "Times New Roman" not in font.name:
                result.add_err(ErrCause.INVALID_FONT, "wrong font name: " + font.name)
                results["font_check"] = False

            # Пример проверки размера (font.size в pt)
            # font.size — объект типа Pt или None, если нет прямого указания
            if font.size:
                # font.size is in English Metric Units (points = 1/72 inch)
                font_size_pt = font.size.pt
                if not (12.01 <= font_size_pt <= 14.01):
                    result.add_err(ErrCause.INVALID_FONT_SIZE, "wrong font size: " + font.size)
                    results["font_size_check"] = False

            # Пример проверки цвета (font.color.rgb)
            # Если цвет не указан, font.color может быть None
            # или <Element ...> без поля rgb
            if font.color and font.color.rgb:
                # Проверяем, что это действительно чёрный (#000000)
                if font.color.rgb != BLACK:
                    result.add_err(ErrCause.INVALID_FONT_COLOR, "wrong color rgb: " + str(font.color.rgb))
                    results["color_check"] = False

        # Проверка выравнивания параграфа (para.alignment)
        # Значения: WD_ALIGN_PARAGRAPH.LEFT, CENTER, RIGHT, JUSTIFY
        if para.alignment is not None:
            # Для выравнивания по ширине — JUSTIFY
            # (значение обычно = 3)
            # нужно from docx.enum.text import WD_ALIGN_PARAGRAPH
            if para.alignment not in (WDAP.JUSTIFY, WDAP.CENTER):
                result.add_err(ErrCause.INVALID_TEXT_ALIGNMENT, para.alignment)
                results["alignment_check"] = False

        # Межстрочный интервал (line_spacing)
        # python-docx позволяет смотреть para.paragraph_format.line_spacing
        # Но часто бывает None, если не задали явно
        # (наследуется из общей стилевой настройки).
        line_spacing = para.paragraph_format.line_spacing
        if line_spacing:
            # Обычно 1.5 = 1.5. Если это значение не совпадает,
            # считаем, что нет нужного интервала
            # (проверка строго по вашему критерию)
            if abs(line_spacing - 1.5) > 0.1:
                result.add_err(ErrCause.INVALID_LINE_SPACING, line_spacing)
                results["line_spacing_check"] = False
    if not(doc_contains_only_tnr(doc)):
        result.add_err(ErrCause.INVALID_FONT, "incorrect font")
    return results


