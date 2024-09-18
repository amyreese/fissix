#!/bin/bash

set -e

finish() {
    set +x
    echo $2
    exit $1
}

if [[ ! -d "fissix" ]]; then
    finish 1 "ERROR: Must be run from root of fissix repository"
fi

# debug mode
set -x

# make sure no local changes
git update-index -q --refresh
if ! git diff-index --quiet HEAD --; then
    finish 1 "ERROR: local changes present; stash or commit then retry"
fi

# switch to base branch, and discard local commits
git checkout -f base
git reset --hard origin/base

# update cpython to latest 3.12
git submodule update --init
git -C cpython checkout -f 3.12
git -C cpython clean -xfd

# copy from cpython
rsync -av cpython/Lib/lib2to3/ fissix/

# reformat lib2to3, ignore any failures
.venv/bin/python -m black --fast fissix/ || true

# Stop early if no changes
git update-index -q --refresh
if git diff-index --quiet HEAD --; then
    git checkout -f main
    finish 0 "DONE: No upstream changes to lib2to3"
fi

# checkpoint on base branch
REV=$(git -C cpython describe)
git commit -am "Import upstream lib2to3 from $REV"

# cherry-pick this to main branch
git checkout -f main
if ! git cherry-pick base --no-commit; then
    while ! git update-index --refresh; do
        read -p "Merge conflicts present; resolve then press Enter to continue" choice
        echo "checking ..."
    done
fi

# reformat to catch merge conflicts
.venv/bin/python -m black --fast fissix/ || true

# Update version markers
scripts/version.sh

# Amend formatting and version markers to cherry-pick commit
git commit -am "Merge upstream lib2to3 from $REV"

finish 0 "Update completed; be sure to push both main and base branches"
