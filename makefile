setup:
	python3 -m pip install -U black
dev:
	python3 setup.py develop

.PHONY: cpython
cpython:
	git submodule update --init
	git -C cpython checkout -f master
	git -C cpython clean -xfd

update: cpython
	git stash && git checkout base
	rsync -av cpython/Lib/lib2to3/ fissix/
	black --fast fissix/

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

lint:
	python3 -m black --check .
	python3 -m pylint --rcfile .pylint edi tests
	-python3 -m mypy --python-version 3.6 .

test:
	python3 -m unittest tests

clean:
	rm -rf build dist *.egg-info .venv .mypy_cache
