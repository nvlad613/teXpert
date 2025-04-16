import re


def convert_to_mm(value_str):
    value_str = value_str.strip()
    while value_str and value_str[0] in '{[':
        value_str = value_str[1:].strip()
    while value_str and value_str[-1] in '}]':
        value_str = value_str[:-1].strip()

    match = re.match(r'^\s*([0-9.]+)\s*([a-zA-Z]+)\s*$', value_str)
    if not match:
        return 0
    number = float(match.group(1))
    unit = match.group(2).lower()
    if unit == 'mm':
        return number
    elif unit == 'cm':
        return number * 10
    elif unit == 'in':
        return number * 25.4
    elif unit == 'pt':
        return number * 0.3514598
    else:
        return 0