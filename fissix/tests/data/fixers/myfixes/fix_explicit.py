from fissix.fixer_base import BaseFix


class FixExplicit(BaseFix):
    explicit = True

    def match(self):
        return False
