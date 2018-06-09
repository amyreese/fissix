from fissix.fixer_base import BaseFix


class FixPreorder(BaseFix):
    order = "pre"

    def match(self, node):
        return False
