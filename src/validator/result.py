from enum import Enum, auto

class ErrCause(Enum):
    INVALID_LATEX_SYNTAX = auto()

    # Шрифт всего документа Times New Roman
    INVALID_FONT = auto()
    # Цвет шрифта - черный
    INVALID_FONT_COLOR = auto()
    # Размер шрифта незаголовочного текста 12-14пт
    INVALID_FONT_SIZE = auto()
    # Поля: левое 30мм, правое 10мм или 15мм, верхнее и нижнее 20мм
    INVALID_PAGE_FIELDS = auto()
    # Абзацный отступ (отступ первого слова в абзаце) незаголовочного текста 1.25см
    INVALID_PARAGRAPH_INDENT = auto()
    # Межстрочный интервал текста - 1.5 строчки
    INVALID_LINE_SPACING = auto()
    # Выравнивание текста по ширине
    INVALID_TEXT_ALIGNMENT = auto()

class ValidationResult:
    errors: dict[ErrCause, str]
    warnings: dict[ErrCause, str]
    log: list[str]

    def __init__(self, errors: dict[ErrCause, str], warning: dict[ErrCause, str], log: list[str]):
        self.errors = errors
        self.warnings = warning
        self.log = log

    @classmethod
    def empty(cls):
        return cls({}, {}, [])

    @classmethod
    def latex(cls):
        """
        Некоторые ошибки добавляются не по ходу проверок, а сразу при создании результата.
        В случае, если ошибка опровергается во время проверок, она удаляется через del_err()
        """
        errors = {
            ErrCause.INVALID_PAGE_FIELDS: "не установлены размеры полей",
            ErrCause.INVALID_PARAGRAPH_INDENT: "абзацный отступ не установлен",
            ErrCause.INVALID_FONT_SIZE: "не установлен корректный размер шрифта"
        }
        warnings = {
            ErrCause.INVALID_FONT: "не определен основной шрифт документа",
            ErrCause.INVALID_LINE_SPACING: "не уставновлен полуторный межстрочный интервал"
        }

        return cls(errors, warnings, [])

    def __init_log(self):
        self.log = []

    def add_err(self, err_type: ErrCause, description: str):
        self.errors[err_type] = description

    def del_warn(self, err_type: ErrCause):
        if err_type in self.warnings:
            self.warnings.pop(err_type)

    def del_err(self, err_type: ErrCause):
        if err_type in self.errors:
            self.errors.pop(err_type)

    def add_warn(self, err_type: ErrCause, description: str):
        self.warnings[err_type] = description

    def log(self, log_str: str):
        self.log.append(log_str)

    def has_err(self) -> bool:
        return len(self.errors.keys()) > 0