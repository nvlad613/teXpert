from __future__ import annotations

"""Simple human‑friendly renderer for ValidationResult objects.

Usage
-----
>>> from reporter import print_report
>>> res: ValidationResult = some_validator()
>>> print_report(res, source="thesis.docx")

If you validate several files at once:
>>> mapping = {filepath: result, ...}
>>> print_batch_report(mapping)

The output is pure UTF‑8 text, so it looks good both in colour‑capable
terminals and in plain text logs.
"""

from enum import Enum
from typing import Dict, Mapping, Iterable, Tuple

try:
    # optional – nice colours if the terminal supports them
    from colorama import Fore, Style, init as _color_init  # type: ignore

    _color_init(autoreset=True)

    def _green(s: str) -> str:
        return f"{Fore.GREEN}{s}{Style.RESET_ALL}"

    def _red(s: str) -> str:
        return f"{Fore.RED}{s}{Style.RESET_ALL}"

    def _yellow(s: str) -> str:
        return f"{Fore.YELLOW}{s}{Style.RESET_ALL}"

except ModuleNotFoundError:  # fallback to monochrome

    def _green(s: str) -> str:  # type: ignore[return-value]
        return s

    def _red(s: str) -> str:  # type: ignore[return-value]
        return s

    def _yellow(s: str) -> str:  # type: ignore[return-value]
        return s

# ──────────────────────────────────────────────────────────────────────────────
# import here to avoid circular refs in type‑check time
from src.validator.result import ValidationResult, ErrCause  # noqa: E402

_SECTION_LINE = "─" * 72


# helpers ─────────────────────────────────────────────────────────────────────

def _fmt_reason(name: Enum) -> str:
    """Convert enum member like INVALID_FONT_SIZE into readable text."""
    return name.name.replace("_", " ").title()


def _iter_dict(d: Mapping[Enum, str]) -> Iterable[Tuple[str, str]]:
    for k, v in d.items():
        yield _fmt_reason(k), v


# public API ───────────────────────────────────────────────────────────────────

def format_single(result: ValidationResult, *, source: str | None = None) -> str:
    """Return formatted multi‑line string for single ValidationResult."""

    lines: list[str] = []
    if source:
        lines.append(_SECTION_LINE)
        lines.append(f"📄  {source}")
        lines.append(_SECTION_LINE)

    # errors
    if result.errors:
        lines.append(_red("✖  Errors:"))
        for i, (reason, msg) in enumerate(_iter_dict(result.errors), 1):
            lines.append(f"   {i}. {_red(reason)} — {msg}")
    else:
        lines.append(_green("✔  Errors not found."))

    # warnings
    if result.warnings:
        lines.append("")
        lines.append(_yellow("⚠  Warnings:"))
        for i, (reason, msg) in enumerate(_iter_dict(result.warnings), 1):
            lines.append(f"   {i}. {_yellow(reason)} — {msg}")
    else:
        lines.append(_green("ℹ  Warnings not found."))

    return "\n".join(lines)


def print_report(result: ValidationResult, *, source: str | None = None) -> None:
    """Print nicely formatted report for a single file."""
    print(format_single(result, source=source))


def print_batch_report(results: Mapping[str, ValidationResult]) -> None:
    """Print reports for many files sequentially with separators."""
    for i, (path, res) in enumerate(results.items()):
        print_report(res, source=path)
        if i + 1 < len(results):
            print()  # blank line between reports
