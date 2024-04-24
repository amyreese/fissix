EXTRAS:=dev,docs
.venv:
	python -m venv .venv
	source .venv/bin/activate && make install

venv: .venv

install:
	python -m pip install -U pip
	python -m pip install -Ue .[$(EXTRAS)]

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

.PHONY: html
html: .venv
	.venv/bin/sphinx-build -ab html docs html 

release: lint test clean
	python -m flit publish

format:
	python -m black fissix tests

lint:
	python -m black --check fissix tests

test:
	python -m pytest --verbose tests fissix/tests

clean:
	rm -rf build dist html *.egg-info .mypy_cache

distclean:
	rm -rf .venv
