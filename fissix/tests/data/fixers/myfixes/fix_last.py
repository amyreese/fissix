from fissix.fixer_base import BaseFix


class FixLast(BaseFix):

    run_order = 10

    def match(self, node):
        return False
