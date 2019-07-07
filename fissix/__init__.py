# copyright 2018 John Reese
# Licensed under the PSF license V2

"""
Monkeypatches to override default behavior of lib2to3.
"""

import logging
import os
import tempfile
from pathlib import Path

from appdirs import user_cache_dir

from .pgen2 import driver, grammar, pgen

__version__ = "19.3"
__base_version__ = "3.8.0a2+"
__base_revision__ = "v3.8.0a2-22-ged1deb0719"

CACHE_DIR = Path(user_cache_dir("fissix", version=__version__))


def _generate_pickle_name(gt):
    path = Path(gt)
    filename = "{}{}.pickle".format(path.stem, __base_version__)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return (CACHE_DIR / filename).as_posix()


def load_grammar(gt="Grammar.txt", gp=None, save=True, force=False, logger=None):
    """Load the grammar (maybe from a pickle)."""
    if logger is None:
        logger = logging.getLogger()
    gp = _generate_pickle_name(gt) if gp is None else gp
    if force or not driver._newer(gp, gt):
        logger.info("Generating grammar tables from %s", gt)
        g = pgen.generate_grammar(gt)
        if save:
            logger.info("Writing grammar tables to %s", gp)
            # Change here...
            with tempfile.TemporaryDirectory(dir=os.path.dirname(gp)) as d:
                tempfilename = os.path.join(d, os.path.basename(gp))
                try:
                    g.dump(tempfilename)
                    os.rename(tempfilename, gp)
                except OSError as e:
                    logger.info("Writing failed: %s", e)
    else:
        g = grammar.Grammar()
        g.load(gp)
    return g


driver._generate_pickle_name = _generate_pickle_name
driver.load_grammar = load_grammar
