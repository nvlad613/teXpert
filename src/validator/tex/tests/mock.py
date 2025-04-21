
class MockLatexMacroNode:
    def __init__(self, macroname, nodeargs=None, nodeoptarg=None):
        self.macroname = macroname
        self.nodeargs = nodeargs or []
        self.nodeoptarg = nodeoptarg

    def latex_verbatim(self):
        return self.macroname