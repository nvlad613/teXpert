from pylatexenc.latexwalker import LatexWalker, get_default_latex_context_db
from pylatexenc.macrospec import MacroSpec

_LATEX_CONTEXT = get_default_latex_context_db()
_LATEX_CONTEXT.add_context_category(
    'my-macros',
    prepend=True,
    macros=[
        MacroSpec("setmainfont", "{"),
        MacroSpec("textcolor", "{"),
        MacroSpec("color", "{"),
        MacroSpec("geometry", "{"),
    ]
)

def parse_latex_structure(latex_content: str) -> list:
    walker = LatexWalker(latex_content, latex_context=_LATEX_CONTEXT)
    nodes, pos, len_ = walker.get_latex_nodes()

    return nodes

def extract_mandatory_args(node):
    args = []
    if hasattr(node, 'nodeargs') and node.nodeargs is not None:
        for arg in node.nodeargs:
            # Если аргумент имеет метод latex_verbatim, используем его
            if hasattr(arg, 'latex_verbatim'):
                args.append(arg.latex_verbatim())
            # Если аргумент является текстовым узлом с атрибутом .chars
            elif hasattr(arg, 'chars'):
                args.append(arg.chars)
            # В противном случае, пробуем привести к строке
            else:
                args.append(str(arg))
    return args

def extract_optional_arg(node):
    if hasattr(node, 'nodeoptarg') and node.nodeoptarg is not None:
        return node.nodeoptarg.latex_verbatim()
    return None
