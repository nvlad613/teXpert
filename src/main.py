import os
from src.validator.pdf.open_doc import open_pdf, validate_pdf
from src.validator.docx.start_checks import start_check_docx_file
from src.validator.result import ValidationResult
from src.validator.tex.parser import parse_latex_structure
from src.validator.tex.treverse_nodes import traverse_nodes


def run_validate_word(filepath):
    result = start_check_docx_file(filepath)
    print(f"Results for {filepath}:")
    print("Warnings:", result.warnings)
    print("Errors:", result.errors)


def run_validate_pdf(filepath):
    pdf = open_pdf(filepath)
    result = validate_pdf(pdf)
    print(result.warnings)
    print(result.errors)


def validate_files(filepaths):
    for filepath in filepaths:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File does not exist: {filepath}")
            continue

        if filepath.lower().endswith('.tex'):
            run_validate_latex(filepath)
        elif filepath.lower().endswith(('.doc', '.docx')):
            run_validate_word(filepath)

        # Always validate PDF file if it exists
        pdf_filepath = os.path.splitext(filepath)[0] + '.pdf'
        if os.path.exists(pdf_filepath):
            run_validate_pdf(pdf_filepath)
        else:
            print(f"No PDF found for {filepath}")


def get_filepaths_to_validate():
    choice = input("Do you want to validate a (1) single file or (2) an entire directory? Enter 1 or 2: ")

    if choice == '1':
        filepath = input("Enter the path of the file to validate: ")
        return [filepath]
    elif choice == '2':
        dirpath = input("Enter the directory path to validate: ")
        return [os.path.join(dirpath, filename) for filename in os.listdir(dirpath) if
                filename.endswith(('.tex', '.doc', '.docx'))]
    else:
        print("Invalid choice. Exiting.")
        exit(1)


def main():
    print("Welcome to the automated file validation tool!")

    # Get list of file paths to validate
    filepaths = get_filepaths_to_validate()

    validate_files(filepaths)


if __name__ == "__main__":
    main()
