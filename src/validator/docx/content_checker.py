import re
from typing import Dict, List, Set
import docx
from docx.enum.style import WD_STYLE_TYPE

STOP_WORDS = {"ЗАКЛЮЧЕНИЕ", "ПРИЛОЖЕНИЕ", "СПИСОК", "ВВЕДЕНИЕ"}

def _clean(line: str) -> str:
    # убираем «…. 15» в конце
    return re.sub(r"\.{2,}\s*\d+\s*$", "", line).strip(" .\t")

def extract_toc_headings(doc: docx.Document) -> List[str]:
    """
    Возвращает список пунктов оглавления из Word‑документа.
    Работает и с англ. (TOC) и с рус. («Оглавление …») стилями.
    """
    toc_headings: List[str] = []
    grab = False

    for p in doc.paragraphs:
        style = (p.style.name or "").strip() if p.style else ""
        text  = p.text.strip()

        # ── начало оглавления ───────────────────────────
        if not grab:
            if style in ("TOC Heading", "Оглавление") or "СОДЕРЖАНИЕ" in text.upper():
                grab = True
            continue

        # ── пункты оглавления ───────────────────────────
        if style.startswith(("TOC", "Оглавление")):   # «TOC 1», «Оглавление 1» …
            if text:
                toc_headings.append(_clean(text))
            continue

        # ── выход из блока оглавления ──────────────────
        if text.upper() in STOP_WORDS:                # Введение, Заключение …
            break

    return toc_headings
def _clean(line: str) -> str:
    return re.sub(r"\.{2,}\s*\d+\s*$", "", line).strip()

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.casefold()).strip()

def extract_and_check_headings_from_docx(doc :docx.Document()) -> Dict:

    toc = extract_toc_headings(doc)
    if not toc:
        return {"status": "failed",
                "reason": "Оглавление (TOC) не найдено",
                "missing_headings": []}

    # собираем реальные заголовки по стилям Heading
    real: Set[str] = set()
    for p in doc.paragraphs:
        if p.style and p.style.name.startswith(("Heading", "Заголовок")):
            real.add(_norm(p.text))

    missing = [h for h in toc if _norm(h) not in real]

    if missing:
        return {"status": "failed",
                "reason": "Некоторые заголовки из содержания не найдены.",
                "missing_headings": missing}
    return {"status": "passed",
            "message": "Все заголовки из содержания присутствуют."}

