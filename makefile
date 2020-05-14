.venv:
	python -m venv .venv
	source .venv/bin/activate && make setup

setup:
	python -m pip install -r requirements.txt
	python -m pip install -r requirements-dev.txt
	python -m flit install --symlink

.PHONY: cpython
cpython:
	git submodule update --init
	git -C cpython checkout -f master
	git -C cpython clean -xfd

.PHONY: version
version:
	scripts/version.sh

.PHONY: update
update: .venv
	scripts/update.sh

release: lint test clean
	flit publish

black:
	python -m black fissix tests
	python -m isort -rc fissix/__init__.py tests/

lint:
	python -m black --check fissix tests

test:
	python -m unittest --verbose tests

clean:
	rm -rf build dist *.egg-info .venv .mypy_cache
