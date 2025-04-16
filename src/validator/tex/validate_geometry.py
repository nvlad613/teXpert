import re

from src.validator.result import ValidationResult, ErrCause
from src.validator.tex.parser import extract_mandatory_args, extract_optional_arg
from src.validator.util import convert_to_mm


def __clean_geometry_arg(arg_string):
    no_comments = re.sub(r'%.*', '', arg_string)
    no_comments = no_comments.strip()
    if no_comments.startswith('{') and no_comments.endswith('}'):
        no_comments = no_comments[1:-1]
    if no_comments.startswith('[') and no_comments.endswith(']'):
        no_comments = no_comments[1:-1]
    parts = [item.strip() for item in no_comments.split(',') if item.strip()]
    return parts

def __validate_geometry_args(args, r: ValidationResult):
    geometry = {
        "right": 0,
        "left": 0,
        "top": 0,
        "bottom": 0
    }
    for arg in __clean_geometry_arg(args[0]):
        a = arg.split("=")
        if len(a) < 2:
            continue
        geometry[a[0]] = convert_to_mm(a[1])

    err = ""
    if not int(geometry["right"]) in [10, 15]:
        err += "некорректное правое поле; "
    if not int(geometry["left"]) in [30]:
        err += "некорректное левое поле; "
    if not int(geometry["top"]) in [20]:
        err += "некорректное верхнее поле; "
    if not int(geometry["bottom"]) in [20]:
        err += "некорректное нижнее поле; "

    if err == "":
        r.del_err(ErrCause.INVALID_PAGE_FIELDS)
    else:
        r.add_err(ErrCause.INVALID_PAGE_FIELDS, err)

def validate_geometry(node, r: ValidationResult):
    if node.macroname == "usepackage":
        args = extract_mandatory_args(node)
        if args and 'geometry' in args[0]:
            opt = extract_optional_arg(node)
            if opt:
                __validate_geometry_args(opt, r)
    if node.macroname == "geometry":
        args = extract_mandatory_args(node)
        if args:
            __validate_geometry_args(args, r)