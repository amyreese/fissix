setup:
	python3 -m pip install -Ur requirements.txt
	python3 -m pip install -U black

dev:
	python3 setup.py develop

.PHONY: cpython
cpython:
	git submodule update --init
	git -C cpython checkout -f master
	git -C cpython clean -xfd

version:
	export VERSION=$$(awk -F '"' '/#define PY_VERSION /{print $$2}' cpython/Include/patchlevel.h) && \
	sed -i "" -e "s/__base_version__ = \".*\"/__base_version__ = \"$$VERSION\"/" fissix/__init__.py
	export VERSION=$$(git -C cpython describe) && \
	sed -i "" -e "s/__base_revision__ = \".*\"/__base_revision__ = \"$$VERSION\"/" fissix/__init__.py

update: cpython version
	git stash && git checkout base
	rsync -av cpython/Lib/lib2to3/ fissix/
	black --fast fissix/

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

black:
	python3 -m black fissix tests setup.py

lint:
	python3 -m black --check fissix tests setup.py

test:
	python3 -m unittest --verbose tests

clean:
	rm -rf build dist *.egg-info .venv .mypy_cache
