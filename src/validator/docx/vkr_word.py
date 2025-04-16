import re
from typing import Dict, Any, List
import docx


def load_docx_text(docx_path: str) -> str:
    """
    Извлекает весь текст из .docx-файла.
    Возвращает конкатенированные строки всех параграфов.
    """
    doc = docx.Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        # Собираем текст, можно между параграфами ставить \n
        full_text.append(para.text)
    return '\n'.join(full_text)


def check_mandatory_sections(doc_text: str) -> Dict[str, bool]:
    """
    Проверка на наличие обязательных разделов:
    1) СОДЕРЖАНИЕ
    2) ЗАКЛЮЧЕНИЕ
    3) СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ
    4) ПРИЛОЖЕНИЕ (А, Б, и т.д.)
    """
    results = {}

    pattern_soderzhanie = re.compile(r"\bсодержание\b", re.IGNORECASE)
    pattern_zakl = re.compile(r"\bзаключение\b", re.IGNORECASE)
    pattern_references = re.compile(r"\bсписок\s+использованных\s+источников\b", re.IGNORECASE)
    pattern_app = re.compile(r"\bприложение\s+[А-ЯA-Zа-яa-z]", re.IGNORECASE)

    results["СОДЕРЖАНИЕ"] = bool(pattern_soderzhanie.search(doc_text))
    results["ЗАКЛЮЧЕНИЕ"] = bool(pattern_zakl.search(doc_text))
    results["СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"] = bool(pattern_references.search(doc_text))
    results["ПРИЛОЖЕНИЕ"] = bool(pattern_app.search(doc_text))

    return results


def extract_toc_headings(doc_text: str) -> List[str]:
    """
    Условная логика для извлечения заголовков из "СОДЕРЖАНИЯ".
    Похожая на пример для PDF:
     - Находим "СОДЕРЖАНИЕ"
     - Берём несколько строк после него
     - Останавливаемся, когда видим большой раздел "Заключение" и т.д.
    """
    toc_headings = []
    match = re.search(r'(содержание)', doc_text, re.IGNORECASE)
    if not match:
        return toc_headings

    start_index = match.end()
    snippet = doc_text[start_index: start_index + 3000]  # ограниченный фрагмент
    lines = snippet.split('\n')

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        # Проверяем, не достигли ли мы другого раздела
        if re.search(r"\b(заключение|приложение|список\s+использованных\s+источников)\b",
                     line_clean, re.IGNORECASE):
            break
        toc_headings.append(line_clean)
    return toc_headings


def extract_document_headings(doc_text: str) -> List[str]:
    """
    Упрощённое выделение заголовков из тела:
     - Считаем, что заголовок — короткая строка с заглавной буквы и без точки в конце.
    """
    lines = doc_text.split('\n')
    headings = []
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        if (len(line_clean) < 100
                and re.match(r'^[A-ZА-Я]', line_clean)
                and not line_clean.endswith('.')):
            headings.append(line_clean)
    return headings


def normalize_heading(heading: str) -> str:
    """
    Простейшая нормализация (убираем регистр и лишние пробелы).
    """
    heading = heading.lower().strip()
    heading = re.sub(r'\s+', ' ', heading)
    return heading


def check_toc_vs_body(toc_headings: List[str], body_headings: List[str]) -> Dict[str, Any]:
    """
    Проверяем, что все заголовки из содержания есть в теле
    и следуют в том же порядке.
    """
    result = {
        "all_present": True,
        "order_correct": True,
        "missing_headings": [],
    }

    current_index = 0
    for toc_h in toc_headings:
        found = False
        for i in range(current_index, len(body_headings)):
            if normalize_heading(body_headings[i]) == normalize_heading(toc_h):
                found = True
                current_index = i + 1
                break
        if not found:
            result["all_present"] = False
            result["missing_headings"].append(toc_h)

    return result


def check_references_format(doc_text: str) -> Dict[str, Any]:
    """
    Условная проверка оформления списка источников:
     - Ссылки в тексте: [1], [2], ...
     - В "СПИСКЕ ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ" — "1.", "2.", ...
     - Сравниваем порядок.
    """
    result = {
        "found_in_text": [],
        "found_in_list": [],
        "order_match": True,
    }
    found_in_text = re.findall(r'\[(\d+)\]', doc_text)
    found_in_text = list(map(int, found_in_text))
    result["found_in_text"] = found_in_text

    match = re.search(r'(список\s+использованных\s+источников)', doc_text, re.IGNORECASE)
    if not match:
        # Раздел не найден, возвращаем пустоту
        return result

    start_index = match.end()
    snippet = doc_text[start_index: start_index + 5000]
    found_in_list = re.findall(r'^\s*(\d+)\.\s', snippet, flags=re.MULTILINE)
    found_in_list = list(map(int, found_in_list))
    result["found_in_list"] = found_in_list

    if len(found_in_text) != len(found_in_list):
        result["order_match"] = False
    else:
        for i, ref_num in enumerate(found_in_text):
            if ref_num != found_in_list[i]:
                result["order_match"] = False
                break

    return result


def check_formatting(docx_path: str) -> Dict[str, Any]:
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

    doc = docx.Document(docx_path)

    # Пример: проверка первого секционного размета на поля
    section = doc.sections[0]
    # Ширина левого поля (section.left_margin) хранится в EMU (English Metric Units)
    # 1 дюйм = 914400 EMU, 1 см = 360000 EMU
    # Нужно переводить EMU в мм.
    # Для проверки «левое поле = 30 мм»:
    left_margin_mm = section.left_margin / 360000.0
    # Допустим, если оно сильно отклоняется от 30, считаем ошибкой
    if not (29.5 <= left_margin_mm <= 30.5):
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
                results["font_check"] = False

            # Пример проверки размера (font.size в pt)
            # font.size — объект типа Pt или None, если нет прямого указания
            if font.size:
                # font.size is in English Metric Units (points = 1/72 inch)
                font_size_pt = font.size.pt
                if not (12 <= font_size_pt <= 14):
                    results["font_size_check"] = False

            # Пример проверки цвета (font.color.rgb)
            # Если цвет не указан, font.color может быть None
            # или <Element ...> без поля rgb
            if font.color and font.color.rgb:
                # Проверяем, что это действительно чёрный (#000000)
                if font.color.rgb != '000000':
                    results["color_check"] = False

        # Проверка выравнивания параграфа (para.alignment)
        # Значения: WD_ALIGN_PARAGRAPH.LEFT, CENTER, RIGHT, JUSTIFY
        if para.alignment is not None:
            # Для выравнивания по ширине — JUSTIFY
            # (значение обычно = 3)
            # нужно from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            if para.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY:
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
                results["line_spacing_check"] = False

    return results


def analyze_docx(docx_path: str) -> Dict[str, Any]:
    """
    Основная функция проверки структуры и форматирования
    для docx (аналогично PDF-примеру).
    """
    # 1. Извлекаем текст
    doc_text = load_docx_text(docx_path)

    # 2. Обязательные разделы
    mandatory_sections = check_mandatory_sections(doc_text)

    # 3. Заголовки: Содержание vs Тело
    toc_headings = extract_toc_headings(doc_text)
    body_headings = extract_document_headings(doc_text)
    toc_vs_body = check_toc_vs_body(toc_headings, body_headings)

    # 4. Список источников
    references_result = check_references_format(doc_text)

    # 5. Форматирование (шрифт, кегль, поля, выравнивание)
    formatting_result = check_formatting(docx_path)

    results = {
        "Обязательные разделы": mandatory_sections,
        "Содержание vs Текст": toc_vs_body,
        "Список источников": references_result,
        "Форматирование": formatting_result
    }
    return results


from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.enum.style import WD_STYLE_TYPE


def get_effective_fontname(doc: docx.Document, para: docx.text.paragraph.Paragraph, run: docx.text.run.Run) -> str:
    """
    Возвращает реальное имя шрифта, которое применяется к данному run,
    учитывая наследование стилей:
      1) run.font.name
      2) run.style.font.name
      3) para.style.font.name
      4) base_style, поднимаясь вверх
      5) doc.styles['Normal'].font.name
    Если нигде не прописано — вернёт None (что означает «в документе явно не указано»).
    """
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


def doc_contains_only_tnr(docx_path: str) -> bool:
    """
    Проверяет, что во всех run документа .docx используется (явно или наследуется)
    шрифт Times New Roman (если run вообще имеет указанное имя шрифта).
    Если найдёт run, у которого эффективное имя шрифта — не Times New Roman,
    возвращает False.

    Если обнаружится, что font = None (т.е. не прописан НИКАК),
    по жёстким критериям тоже можно считать, что документ не соответствует
    требованию "только Times New Roman", т.к. явно не прописан.

    Но это поведение можно изменить, если вы хотите считать,
    что "не прописан" = "скорее всего Times New Roman".
    """
    doc = docx.Document(docx_path)
    for para in doc.paragraphs:
        for run in para.runs:
            eff_font = get_effective_fontname(doc, para, run)
            print(eff_font)
            if eff_font is None:
                # Если вы хотите допустить, что None = Times New Roman, закомментируйте эту строку:
                return False
            # Здесь проверяем, что строка eff_font действительно содержит "Times New Roman"
            # с учётом возможных вариаций ("Times New Roman CE", "Times New Roman Bold" и т.п.).
            if not re.search(r'times\s*new\s*roman', eff_font, re.IGNORECASE):
                return False
    return True

if __name__ == "__main__":
    # Если у вас doc-файл, сначала нужно сконвертировать в docx,
    # либо вручную, либо внешними инструментами.
    docx_file = "/Users/tix/PycharmProjects/infobez/lab2.1/Вацет Мария P34111_Шаблон.docx"
    report = analyze_docx(docx_file)
    path = "/Users/tix/PycharmProjects/infobez/lab2.1/Вацет Мария P34111_Шаблон.docx"
    print(doc_contains_only_tnr(path))
    import json

    print(json.dumps(report, ensure_ascii=False, indent=2))
