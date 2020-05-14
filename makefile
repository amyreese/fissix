setup:
	python3 -m pip install -Ur requirements.txt
	python3 -m pip install -U black isort

dev:
	python3 setup.py develop

.PHONY: cpython
cpython:
	git submodule update --init
	git -C cpython checkout -f master
	git -C cpython clean -xfd

version:
	scripts/version.sh

update: cpython version
	git stash && git checkout base
	git reset --hard origin/base
	rsync -av cpython/Lib/lib2to3/ fissix/
	python3 -m black --fast fissix/
	git commit -am "Import lib2to3 from $$(git -C cpython describe)"
	git checkout -f master
	git merge base -m "Merge branch 'base' from $$(git -C cpython describe)"
	git stash pop && git commit -am "Update base version/revision from $$(git -C cpython describe)"

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

black:
	python3 -m black fissix tests setup.py
	python3 -m isort -rc fissix/__init__.py tests/ setup.py

lint:
	python3 -m black --check fissix tests setup.py

test:
	python3 -m unittest --verbose tests

clean:
	rm -rf build dist *.egg-info .venv .mypy_cache
