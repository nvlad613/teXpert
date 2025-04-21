from src.validator.result import ValidationResult, ErrCause
from src.validator.tex.tests.mock import MockLatexMacroNode
from src.validator.tex.validate_font_style import validate_parindent
from src.validator.tex.validate_geometry import validate_geometry


def test_geometry_valid():
    node = MockLatexMacroNode('geometry', ['left=30mm,right=10mm,top=20mm,bottom=20mm'])
    result = ValidationResult.latex()
    validate_geometry(node, result)
    assert not result.has_err(ErrCause.INVALID_PAGE_FIELDS)

def test_geometry_invalid():
    node = MockLatexMacroNode('geometry', ['left=35mm,right=10mm,top=20mm,bottom=20mm'])
    result = ValidationResult.latex()
    validate_geometry(node, result)
    assert result.has_err(ErrCause.INVALID_PAGE_FIELDS)

# Тесты для validate_parindent
def test_parindent_valid():
    node = MockLatexMacroNode('setlength', ['\\parindent', '12.5mm'])
    result = ValidationResult.latex()
    validate_parindent(node, result)
    assert not result.has_err(ErrCause.INVALID_PARAGRAPH_INDENT)

def test_parindent_invalid():
    node = MockLatexMacroNode('setlength', ['\\parindent', '10mm'])
    result = ValidationResult.empty()
    validate_parindent(node, result)
    assert ErrCause.INVALID_PARAGRAPH_INDENT in result.errors