import docx
import re


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
