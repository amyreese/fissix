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
html:
	uv run --frozen sphinx-build -ab html docs html

format:
	uv run --frozen ufmt format fissix tests

lint:
	uv run --frozen ufmt check fissix tests

test:
	uv run --frozen pytest --verbose tests fissix/tests

clean:
	rm -rf build dist html *.egg-info .mypy_cache

distclean:
	rm -rf .venv
