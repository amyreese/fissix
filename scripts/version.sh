#!/bin/bash

set -e

export VERSION=$(awk -F '"' '/define PY_VERSION /{print $2}' cpython/Include/patchlevel.h)
perl -i -p -e "s/__base_version__ = \".*\"/__base_version__ = \"$VERSION\"/" fissix/__init__.py

export VERSION=$(git -C cpython describe)
perl -i -p -e "s/__base_revision__ = \".*\"/__base_revision__ = \"$VERSION\"/" fissix/__init__.py
