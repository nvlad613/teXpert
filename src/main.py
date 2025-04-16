from src.validator.result import ValidationResult
from src.validator.tex.parser import parse_latex_structure
from src.validator.tex.treverse_nodes import traverse_nodes


def main():
    validate_latex("/home/vlad/PycharmProjects/latex-validator/test_file.tex")


def validate_latex(filepath):
    with open(filepath, encoding='utf-8') as f:
        latex_content = f.read()
        structure = parse_latex_structure(latex_content)
        result = traverse_nodes(structure)
        print(result.warnings)
        print(result.errors)

if __name__ == "__main__":
    main()