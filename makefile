.venv:
	python -m venv .venv
	.venv/bin/python -m pip install -U pip
	.venv/bin/python -m pip install -r requirements.txt
	.venv/bin/python -m pip install -r requirements-dev.txt
	.venv/bin/python -m pip install -e .

.PHONY: cpython
cpython:
	git submodule update --init
	git -C cpython checkout -f master
	git -C cpython clean -xfd

.PHONY: version
version:
	scripts/version.sh

.PHONY: update
update: .venv cpython version
	git stash && git checkout base
	git reset --hard origin/base
	rsync -av cpython/Lib/lib2to3/ fissix/
	-.venv/bin/python -m black --fast fissix/
	git commit -am "Import lib2to3 from $$(git -C cpython describe)"
	git checkout -f master
	git merge base -m "Merge branch 'base' from $$(git -C cpython describe)"
	git stash pop && git commit -am "Update base version/revision from $$(git -C cpython describe)"

release: lint test clean
	python setup.py sdist
	.venv/bin/python -m twine upload dist/*

black: .venv
	.venv/bin/python -m black fissix tests setup.py
	.venv/bin/python -m isort -rc fissix/__init__.py tests/ setup.py

lint: .venv
	.venv/bin/python -m black --check fissix tests setup.py

test: .venv
	.venv/bin/python -m unittest --verbose tests

clean:
	rm -rf build dist *.egg-info .venv .mypy_cache
