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

.PHONY: update
update:
	python scripts/update.py

.PHONY: check-sync
check-sync:
	python scripts/update.py --check

.PHONY: html
html: .venv
	.venv/bin/sphinx-build -ab html docs html

release: lint test clean
	python -m flit publish

format:
	python -m ufmt format fissix tests

lint:
	python -m ufmt check fissix tests

test:
	python -m pytest --verbose tests fissix/tests

clean:
	rm -rf build dist html *.egg-info .mypy_cache

distclean:
	rm -rf .venv
