from src.validator.pdf.open_doc import open_pdf, validate_pdf
from src.validator.result import ValidationResult
from src.validator.tex.parser import parse_latex_structure
from src.validator.tex.traverse_nodes import traverse_nodes


def main():
    run_pdf_validation("/home/vlad/PycharmProjects/latex-validator/test.pdf")
    run_latex_validation("/home/vlad/PycharmProjects/latex-validator/test_file.tex")

def run_pdf_validation(filepath):
    pdf = open_pdf(filepath)
    result = validate_pdf(pdf)
    print(result.warnings)
    print(result.errors)

def run_latex_validation(filepath):
    with open(filepath, encoding='utf-8') as f:
        latex_content = f.read()
        structure = parse_latex_structure(latex_content)
        result = traverse_nodes(structure)
        print(result.warnings)
        print(result.errors)

if __name__ == "__main__":
    main()