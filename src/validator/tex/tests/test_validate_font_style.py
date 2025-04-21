import pytest

from .mock import MockLatexMacroNode
from src.validator.tex.validate_font_style import *

# Тесты для validate_font_usage
def test_font_whitelist_package():
    node = MockLatexMacroNode('usepackage', ['{times}'])
    result = ValidationResult.latex()
    validate_font_usage(node, result)
    assert ErrCause.INVALID_FONT not in result.warnings

def test_font_setmainfont_valid():
    node = MockLatexMacroNode('setmainfont', ['Times New Roman'])
    result = ValidationResult.empty()
    validate_font_usage(node, result)
    assert ErrCause.INVALID_FONT in result.errors

# Тесты для validate_font_color
def test_font_color_valid():
    node = MockLatexMacroNode('color', ['black'])
    result = ValidationResult.empty()
    validate_font_color(node, result)
    assert not result.errors

def test_font_color_invalid():
    node = MockLatexMacroNode('textcolor', ['red', 'text'])
    result = ValidationResult.empty()
    validate_font_color(node, result)
    assert ErrCause.INVALID_FONT_COLOR in result.errors

# Тесты для validate_font_sz
def test_font_size_valid():
    node = MockLatexMacroNode(
        'documentclass',
        nodeoptarg=MockLatexMacroNode('12pt')
    )
    result = ValidationResult.latex()
    validate_font_sz(node, result)
    assert not result.has_err(ErrCause.INVALID_FONT_SIZE)

# Тесты для validate_line_spacing
def test_line_spacing_valid():
    node = MockLatexMacroNode('onehalfspacing')
    result = ValidationResult.latex()
    validate_line_spacing(node, result)
    assert ErrCause.INVALID_LINE_SPACING not in result.warnings