#!/usr/bin/env python3
"""
add_patch.py — Generate a fissix patch from the HEAD commit.

Usage:
    python scripts/add_patch.py <patch_name>

This script:
1. Identifies which fissix/ files the HEAD commit touched.
2. Builds the unpatched sync baseline (sync without any patches).
3. Diffs the baseline against the committed fissix/ tree for those files.
4. Writes the result to scripts/patches/<patch_name>.patch.
5. Appends the patch to the PATCHES list in scripts/update.py.

The generated patch will apply cleanly when update.py runs its sync
pipeline (copy → rename → format → patch).
"""

from __future__ import annotations

import argparse
import importlib.util
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
PATCHES_DIR = SCRIPTS_DIR / "patches"
UPDATE_PY = SCRIPTS_DIR / "update.py"
FISSIX_DIR = REPO_ROOT / "fissix"


def _import_update():
    """Import scripts/update.py by file path without mutating sys.path."""
    spec = importlib.util.spec_from_file_location("update", UPDATE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_head_fissix_files() -> list[str]:
    """Return fissix/ files changed in HEAD commit (relative to repo root)."""
    output = subprocess.check_output(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD", "--", "fissix/"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [f for f in output.strip().splitlines() if f]


def build_unpatched_base(dest: Path) -> None:
    """Run sync() with no patches to produce the unpatched baseline."""
    update = _import_update()

    saved = update.PATCHES[:]
    update.PATCHES = []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            update.sync(tmp_root)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(tmp_root / "fissix", dest)
    finally:
        update.PATCHES = saved


def generate_patch(base_dir: Path, changed_files: list[str]) -> str:
    """Generate a unified diff patch for the changed files."""
    parts: list[str] = []

    for filepath in sorted(changed_files):
        # filepath is like "fissix/fixes/fix_foo.py"
        rel = filepath.removeprefix("fissix/")
        base_file = base_dir / rel
        work_file = FISSIX_DIR / rel

        if not work_file.exists():
            # File was deleted — skip (deletion patches are unusual)
            continue

        if not base_file.exists():
            # New file
            result = subprocess.run(
                ["git", "diff", "--no-index", "/dev/null", str(work_file)],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            lines = result.stdout.splitlines(True)
            for i, line in enumerate(lines):
                if line.startswith("diff --git"):
                    lines[i] = f"diff --git a/{filepath} b/{filepath}\n"
            parts.append("".join(lines))
        else:
            # Modified file
            result = subprocess.run(
                ["diff", "-u", str(base_file), str(work_file)],
                capture_output=True, text=True,
            )
            lines = result.stdout.splitlines(True)
            if len(lines) >= 2:
                lines[0] = f"--- a/{filepath}\n"
                lines[1] = f"+++ b/{filepath}\n"
            parts.append("".join(lines))

    return "\n".join(parts)


def add_to_patches_list(patch_filename: str) -> bool:
    """Append patch_filename to the PATCHES list in update.py.

    Returns True on success, False if the PATCHES list could not be found.
    """
    content = UPDATE_PY.read_text()

    # Find the PATCHES list and insert before the closing bracket
    pattern = re.compile(r"(PATCHES\s*=\s*\[.*?)(])", re.DOTALL)
    match = pattern.search(content)
    if not match:
        logger.error("Could not find PATCHES list in update.py")
        return False

    before_bracket = match.group(1).rstrip()
    # Check if already present
    if f'"{patch_filename}"' in before_bracket:
        logger.info("%s already in PATCHES list", patch_filename)
        return True

    new_content = content[:match.start()] + before_bracket + f'\n    "{patch_filename}",\n' + match.group(2) + content[match.end():]
    UPDATE_PY.write_text(new_content)
    logger.info("Added %s to PATCHES list in update.py", patch_filename)
    return True


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "patch_name",
        help="Name for the patch (without .patch extension)",
    )
    args = parser.parse_args()

    patch_filename = f"{args.patch_name}.patch"
    patch_path = PATCHES_DIR / patch_filename

    # 1. Find changed fissix/ files in HEAD
    changed = get_head_fissix_files()
    if not changed:
        logger.error("HEAD commit has no changes to fissix/")
        return 1
    logger.info("HEAD commit touches: %s", ", ".join(changed))

    # 2. Build unpatched baseline
    base_dir = Path(tempfile.mkdtemp(prefix="fissix-base-"))
    try:
        logger.info("Building unpatched baseline …")
        build_unpatched_base(base_dir)

        # 3. Generate patch
        logger.info("Generating patch …")
        patch_content = generate_patch(base_dir, changed)
        if not patch_content.strip():
            logger.error("No differences found — HEAD changes may already be in the sync output")
            return 1
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)

    # 4. Write patch file
    PATCHES_DIR.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(patch_content)
    logger.info("Wrote %s", patch_path.relative_to(REPO_ROOT))

    # 5. Add to PATCHES list
    if not add_to_patches_list(patch_filename):
        return 1

    logger.info("Done. Verify with:  python scripts/update.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
