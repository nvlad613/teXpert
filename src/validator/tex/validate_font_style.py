from pylatexenc.latexwalker import LatexMacroNode

from src.validator.result import ValidationResult, ErrCause
from src.validator.tex.parser import extract_mandatory_args, extract_optional_arg
from src.validator.util import convert_to_mm

_WHITELIST_PACKAGES = ['{times}', '{mathptmx}', '{tempora}']

def validate_font_usage(node, r: ValidationResult):
    """
    Проверяем наличие указания на использование Times New Roman:
     - через подключение пакетов (например, times, mathptmx)
     - через команду setmainfont{Times New Roman}
    """
    if node.macroname == "usepackage":
        args = extract_mandatory_args(node)
        if args and args[0] in _WHITELIST_PACKAGES:
            r.del_warn(ErrCause.INVALID_FONT)
    if node.macroname == "setmainfont":
        args = extract_mandatory_args(node)
        if args:
            if args[0] != "Times New Roman":
                r.del_warn(ErrCause.INVALID_FONT)
            else:
                r.add_err(ErrCause.INVALID_FONT, f"{args[0]} установлен в качестве шрифта по умолчанию")

def validate_font_color(node, r: ValidationResult):
    if node.macroname in ['color', 'textcolor']:
        args = extract_mandatory_args(node)
        if args and args[0] != 'black':
            r.add_err(ErrCause.INVALID_FONT_COLOR, f"использован {args[0]} цвет для текста")

def validate_parindent(node, r: ValidationResult):
    if node.macroname == "setlength":
        args = extract_mandatory_args(node)
        if len(args) >= 2 and "parindent" in args[0]:
            if convert_to_mm(args[1]) == 12.5:
                r.del_err(ErrCause.INVALID_PARAGRAPH_INDENT)
            else:
                r.add_err(ErrCause.INVALID_PARAGRAPH_INDENT, f"установлен абзацный отступ {args[1]}")

def validate_font_sz(node, r: ValidationResult):
    if node.macroname == "documentclass":
        opt = extract_optional_arg(node)
        if opt and (('14pt' in opt) or ('12pt' in opt)):
            r.del_err(ErrCause.INVALID_FONT_SIZE)

def validate_line_spacing(node, r: ValidationResult):
    if node.macroname == "onehalfspacing":
        r.del_warn(ErrCause.INVALID_LINE_SPACING)
    if node.macroname == "setstretch":
        args = extract_mandatory_args(node)
        if args and args[0].strip() in ['1.5', '1.50']:
            r.del_warn(ErrCause.INVALID_LINE_SPACING)