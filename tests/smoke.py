# copyright 2018 John Reese
# Licensed under the PSF license V2

import logging
from unittest import TestCase

from fissix import pygram, pytree
from fissix.pgen2 import driver

log = logging.getLogger(__name__)


class SmokeTest(TestCase):
    def setUp(self):
        self.grammar = pygram.python_grammar
        self.driver = driver.Driver(self.grammar, convert=pytree.convert, logger=log)

    def test_parse_string(self):
        code = """
from foo import bar

value = 123
print(bar(f"123"))
        """
        tree = self.driver.parse_string(code)
