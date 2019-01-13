# copyright 2018 John Reese
# Licensed under the PSF license V2

"""
Monkeypatches to override default behavior of lib2to3.
"""

import os
import sys
from pathlib import Path

from appdirs import user_cache_dir

from .pgen2 import driver

__version__ = "19.1b1"
__base_version__ = "3.8.0a0"
__base_revision__ = "v3.7.0a4-1294-ge0b5b2096e"

CACHE_DIR = Path(user_cache_dir("fissix", version=__version__))


def _generate_pickle_name(gt):
    path = Path(gt)
    filename = f"{path.stem}{__base_version__}.pickle"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return (CACHE_DIR / filename).as_posix()


driver._generate_pickle_name = _generate_pickle_name
