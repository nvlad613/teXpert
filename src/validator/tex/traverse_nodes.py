from pylatexenc.latexwalker import LatexWalker, LatexMacroNode, LatexGroupNode, LatexEnvironmentNode, LatexCharsNode

from src.validator.result import ValidationResult
from src.validator.tex.validate_font_style import *
from src.validator.tex.parser import extract_mandatory_args, extract_optional_arg
from src.validator.tex.validate_geometry import validate_geometry


def traverse_nodes(nodelist: list) -> ValidationResult:
    result = ValidationResult.latex()
    __traverse_nodes(nodelist, result)
    return result

def __traverse_nodes(nodelist, r: ValidationResult):
    for node in nodelist:
        if isinstance(node, LatexMacroNode):
            # запускаем все необходимые проверки
            validate_font_usage(node, r)
            validate_font_color(node, r)
            validate_geometry(node, r)
            validate_parindent(node, r)
            validate_font_sz(node, r)
            validate_line_spacing(node, r)

        # Рекурсивный обход для вложенных групп:
        if hasattr(node, 'nodelist') and node.nodelist:
            __traverse_nodes(node.nodelist, r)