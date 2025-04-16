import fitz  # PyMuPDF
import re


def extract_and_check_headings_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)

    toc_page_index = None
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if "СОДЕРЖАНИЕ" in text.upper():
            toc_page_index = i
            break

    if toc_page_index is None:
        return {
            "status": "failed",
            "reason": "Не найдена страница с содержанием (СОДЕРЖАНИЕ)",
            "missing_headings": []
        }

    toc_page_text = doc[toc_page_index].get_text("text")

    toc_lines = [line.strip() for line in toc_page_text.split("\n") if "." in line and len(line.strip()) > 5]
    toc_headings = [re.sub(r"\.+\s*\d+$", "", line).strip() for line in toc_lines]
    all_headings = set()
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    text = " ".join([span["text"] for span in line["spans"]]).strip()
                    fontsize = max(span["size"] for span in line["spans"])
                    if fontsize >= 12 and len(text) > 5:
                        all_headings.add(text)

    heading_presence = {h: any(h in heading for heading in all_headings) for h in toc_headings}
    missing = [h for h, present in heading_presence.items() if not present]
    print(missing)
    if not missing:
        return {
            "status": "passed",
            "message": "Все заголовки из содержания найдены в тексте документа."
        }
    else:
        return {
            "status": "failed",
            "reason": "Некоторые заголовки из содержания не найдены в тексте.",
            "missing_headings": missing
        }