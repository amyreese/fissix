# copyright 2018 John Reese
# Licensed under the PSF license V2

"""
Monkeypatches to override default behavior of lib2to3.
"""

import os
import sys

from .pgen2 import driver

__version__ = "18.6a0"
__base_version__ = "3.8.0a0"
__base_revision__ = "v3.7.0a4-888-g4acc140f8d"


def _generate_pickle_name(gt):
    head, tail = os.path.splitext(gt)
    if tail == ".txt":
        tail = ""
    return head.split("/")[-1] + tail + __base_version__ + ".pickle"


driver._generate_pickle_name = _generate_pickle_name
