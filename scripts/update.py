#!/usr/bin/env python3
"""
update.py - Sync lib2to3 from the cpython submodule into fissix/

Workflow
--------
1. Update the cpython submodule to the latest 3.12 code (branch while
   active, latest tag after EOL).
2. Copy cpython/Lib/lib2to3/ and cpython/Lib/test/test_lib2to3/ into a
   TemporaryDirectory, preserving fissix's own __version__.py.
3. Write fissix/__init__.py with version markers read from the submodule.
4. Replace every ``lib2to3`` identifier with ``fissix`` in all .py files.
5. Format with ufmt (black + usort).
6. Apply the fissix-specific patch files from scripts/patches/ against
   the fully formatted, renamed tree.
7. Copy the result on top of fissix/ in the working tree.
8. Exit 1 if git reports any diff in fissix/ or the cpython submodule
   pointer is out of date – use this as a CI "check" step.

Run with ``--check`` to perform steps 1-7 but treat any resulting diff
as a failure rather than committing.  Without ``--check`` the script
updates fissix/ in place and exits 0 only when the tree was already
clean (no new upstream changes); it exits 1 when changes were written
so the caller knows to stage and commit them.
"""

from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CPYTHON_DIR = REPO_ROOT / "cpython"
FISSIX_DIR = REPO_ROOT / "fissix"
PATCHES_DIR = REPO_ROOT / "scripts" / "patches"

# Patches are applied (with ``patch -p1``) from a directory whose layout
# mirrors the repo root, i.e. the temp working dir contains a ``fissix/``
# sub-directory so that paths like ``fissix/main.py`` resolve correctly.
# Patch headers use ``a/fissix/`` / ``b/fissix/`` (git diff format); -p1
# strips that leading ``a/`` / ``b/`` component.
PATCHES = [
    "tokenize_async_with.patch",
    "main_commonpath.patch",
    "test_all_fixers_polyfill.patch",
    "test_fixers_support_import.patch",
    "test_main_xfail.patch",
    "test_parser_xfail.patch",
]

# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------

_PY_VERSION_RE = re.compile(r'#define\s+PY_VERSION\s+"([^"]+)"')


def _cpython_py_version() -> str:
    text = (CPYTHON_DIR / "Include" / "patchlevel.h").read_text()
    m = _PY_VERSION_RE.search(text)
    if not m:
        raise RuntimeError("Could not parse PY_VERSION from cpython/Include/patchlevel.h")
    return m.group(1)


def _cpython_rev() -> str:
    # Use --abbrev=12 to pin the hash length; the default minimum-unique
    # abbreviation varies between environments and causes spurious diffs.
    return subprocess.check_output(
        ["git", "describe", "--abbrev=12"],
        cwd=CPYTHON_DIR,
        text=True,
    ).strip()


# ---------------------------------------------------------------------------
# __init__.py template
# ---------------------------------------------------------------------------

_INIT_TEMPLATE = '''\
# copyright 2022 Amethyst Reese
# Licensed under the PSF license V2


"""
Monkeypatches to override default behavior of fissix.
"""

import logging
import os
import tempfile
from pathlib import Path

from platformdirs import user_cache_dir

from .__version__ import __version__
from .pgen2 import driver, grammar, pgen

__base_version__ = "{py_version}"
__base_revision__ = "{cpython_rev}"

CACHE_DIR = Path(user_cache_dir("fissix", version=__version__))


def _generate_pickle_name(gt):
    path = Path(gt)
    filename = f"{{path.stem}}{{__base_version__}}.pickle"
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
'''

# ---------------------------------------------------------------------------
# ufmt config written to the temp root so ufmt finds it when walking up
# ---------------------------------------------------------------------------

_UFMT_PYPROJECT = """\
[tool.ufmt]
excludes = [
    "fissix/tests/data/",
]
sorter = "skip"
"""

# ---------------------------------------------------------------------------
# Core sync logic
# ---------------------------------------------------------------------------

_LIB2TO3_RE = re.compile(r"\blib2to3\b")


def sync(tmp_root: Path) -> None:
    """
    Populate *tmp_root/fissix/* with the synced+patched+formatted result.

    The caller is responsible for creating *tmp_root*.  After this function
    returns, ``tmp_root / "fissix"`` contains the complete, ready-to-copy
    fissix package tree.
    """
    tmp_fissix = tmp_root / "fissix"

    # 1a. Copy lib2to3 core (no tests/ subdirectory in 3.12 – they were moved
    #     to Lib/test/test_lib2to3/ in CPython)
    lib2to3_src = CPYTHON_DIR / "Lib" / "lib2to3"
    logger.debug("Copying %s → %s", lib2to3_src, tmp_fissix)
    shutil.copytree(lib2to3_src, tmp_fissix)

    # 1b. Copy tests from their new home in Lib/test/test_lib2to3/
    test_src = CPYTHON_DIR / "Lib" / "test" / "test_lib2to3"
    logger.debug("Copying %s → %s/tests", test_src, tmp_fissix)
    shutil.copytree(test_src, tmp_fissix / "tests")

    # 1c. Preserve __version__.py – fissix-only file managed by attribution,
    #     not present in cpython
    shutil.copy2(FISSIX_DIR / "__version__.py", tmp_fissix / "__version__.py")

    # 2. Write fissix/__init__.py with live version markers
    py_version = _cpython_py_version()
    cpython_rev = _cpython_rev()
    logger.info("cpython version %s (%s)", py_version, cpython_rev)
    (tmp_fissix / "__init__.py").write_text(
        _INIT_TEMPLATE.format(py_version=py_version, cpython_rev=cpython_rev),
        encoding="utf-8",
    )

    # 3. Rename lib2to3 → fissix in every .py file
    logger.debug("Renaming lib2to3 → fissix in .py files")
    for py_file in tmp_fissix.rglob("*.py"):
        original = py_file.read_bytes()
        text = original.decode("utf-8", errors="surrogateescape")
        replaced = _LIB2TO3_RE.sub("fissix", text)
        if replaced != text:
            py_file.write_bytes(replaced.encode("utf-8", errors="surrogateescape"))

    # 4. Write a minimal pyproject.toml so ufmt picks up sorter=skip and
    #    excludes the Python-2 test data files (which are not valid Python 3)
    (tmp_root / "pyproject.toml").write_text(_UFMT_PYPROJECT, encoding="utf-8")

    # 5. Format with ufmt; ignore non-zero exit (Python 2 data files cause
    #    parse errors that ufmt reports but gracefully skips)
    logger.info("Formatting with ufmt …")
    subprocess.run(
        [sys.executable, "-m", "ufmt", "format", str(tmp_fissix)],
        cwd=tmp_root,
    )

    # 6. Apply fissix-specific patches against the formatted, renamed tree.
    #    Patches use ``a/fissix/`` / ``b/fissix/`` paths (-p1 strips the a/b prefix)
    #    and were generated from the formatted baseline, so quote style and
    #    namespace already match.
    for patch_name in PATCHES:
        logger.info("Applying patch %s", patch_name)
        patch_path = PATCHES_DIR / patch_name
        subprocess.run(
            ["patch", "--no-backup-if-mismatch", "-p1", "--input", str(patch_path)],
            cwd=tmp_root,
            check=True,
        )


# ---------------------------------------------------------------------------
# Submodule handling
# ---------------------------------------------------------------------------

def update_submodule() -> None:
    """Advance the cpython submodule to the latest 3.12 code.

    Prefers the ``3.12`` branch (still active while the version is
    maintained).  Once CPython 3.12 reaches end-of-life and the branch is
    deleted, falls back to the latest ``v3.12.*`` release tag so this script
    keeps working without modification.
    """
    subprocess.run(
        ["git", "submodule", "update", "--init"],
        cwd=REPO_ROOT,
        check=True,
    )

    # Fetch both the branch (if it still exists) and all v3.12.* tags.
    subprocess.run(
        [
            "git", "-C", str(CPYTHON_DIR), "fetch",
            "--tags",
            "origin",
            # refspec: fetch the branch tip into a local remote-tracking ref;
            # silently ignored by git if the branch no longer exists
            "+refs/heads/3.12:refs/remotes/origin/3.12",
        ],
        check=True,
    )

    # Prefer the live branch; fall back to the newest tag.
    branch_result = subprocess.run(
        ["git", "-C", str(CPYTHON_DIR), "rev-parse", "--verify", "origin/3.12"],
        capture_output=True,
    )
    if branch_result.returncode == 0:
        target = "origin/3.12"
        logger.info("cpython: using branch origin/3.12")
    else:
        # Branch is gone (post-EOL).  Pick the highest v3.12.x tag.
        tags = subprocess.check_output(
            ["git", "-C", str(CPYTHON_DIR), "tag", "-l", "v3.12.*"],
            text=True,
        ).split()
        if not tags:
            raise RuntimeError(
                "No v3.12.* tags found in cpython remote and branch 3.12 is gone"
            )
        # Sort by version tuple so e.g. v3.12.10 > v3.12.9.
        # Filter to final releases only (x.y.z with all-numeric components)
        # to avoid int() failing on pre-release suffixes like "0a1".
        _final_re = re.compile(r"^v\d+\.\d+\.\d+$")
        final_tags = [t for t in tags if _final_re.match(t)] or tags
        final_tags.sort(key=lambda t: tuple(int(x) for x in t.lstrip("v").split(".")))
        target = final_tags[-1]
        logger.warning("cpython: branch 3.12 not found, using latest tag %s", target)

    subprocess.run(
        ["git", "-C", str(CPYTHON_DIR), "checkout", target],
        check=True,
    )


def submodule_is_dirty() -> bool:
    """Return True if the committed submodule ref differs from HEAD."""
    out = subprocess.check_output(
        ["git", "submodule", "status", "cpython"],
        cwd=REPO_ROOT,
        text=True,
    )
    # A leading '+' means the checked-out commit differs from the index ref
    return out.startswith("+")


# ---------------------------------------------------------------------------
# Diff / copy helpers
# ---------------------------------------------------------------------------

def fissix_has_diff() -> bool:
    """Return True if fissix/ has uncommitted changes (modified or untracked)."""
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", "fissix/"],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return True
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "fissix/"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    return bool(untracked)


def copy_to_fissix(tmp_fissix: Path) -> None:
    """Overwrite FISSIX_DIR with the contents of *tmp_fissix*."""
    # Remove files that have disappeared upstream
    for existing in FISSIX_DIR.rglob("*"):
        if existing.is_file():
            relative = existing.relative_to(FISSIX_DIR)
            if not (tmp_fissix / relative).exists():
                existing.unlink()
    # Copy everything from the temp tree
    shutil.copytree(tmp_fissix, FISSIX_DIR, dirs_exist_ok=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Verify that fissix/ matches what the script would generate from "
            "the *committed* cpython submodule ref. Exits 1 if it does not "
            "(suitable for CI). Does not fetch or advance the submodule."
        ),
    )
    args = parser.parse_args()

    if args.check:
        # Check mode: use the committed submodule ref as-is.  Initialise it
        # and unshallow if needed so that git describe has access to tag
        # history (CI checks out submodules with --depth=1).
        subprocess.run(
            ["git", "submodule", "update", "--init"],
            cwd=REPO_ROOT,
            check=True,
        )
        is_shallow = subprocess.check_output(
            ["git", "-C", str(CPYTHON_DIR), "rev-parse", "--is-shallow-repository"],
            text=True,
        ).strip()
        if is_shallow == "true":
            logger.info("cpython submodule is shallow; unshallowing for git describe …")
            subprocess.run(
                ["git", "-C", str(CPYTHON_DIR), "fetch", "--unshallow"],
                check=True,
            )
        with tempfile.TemporaryDirectory() as _tmp:
            tmp_root = Path(_tmp)
            logger.info("Syncing lib2to3 into temporary directory …")
            sync(tmp_root)
            tmp_fissix = tmp_root / "fissix"
            logger.info("Copying result to %s …", FISSIX_DIR)
            copy_to_fissix(tmp_fissix)

        if fissix_has_diff():
            logger.error(
                "fissix/ is out of sync with the cpython submodule.\n"
                "Run  python scripts/update.py  and commit the result."
            )
            return 1
        logger.info("OK: fissix/ is in sync.")
        return 0

    # Update mode: advance the submodule to the latest 3.12 code first.
    logger.info("Updating cpython submodule to 3.12 …")
    update_submodule()

    with tempfile.TemporaryDirectory() as _tmp:
        tmp_root = Path(_tmp)
        logger.info("Syncing lib2to3 into temporary directory …")
        sync(tmp_root)
        tmp_fissix = tmp_root / "fissix"
        logger.info("Copying result to %s …", FISSIX_DIR)
        copy_to_fissix(tmp_fissix)

    # Exit 1 when changes were written so the caller knows to stage and commit
    # both fissix/ and the updated cpython submodule pointer.
    if fissix_has_diff() or submodule_is_dirty():
        logger.info("Changes written to fissix/. Stage and commit them.")
        return 1

    logger.info("No changes – fissix/ was already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
