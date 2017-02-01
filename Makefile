.PHONY: coverage test test3.5 test_first_fail clean autopep8 lint doc-html

COV_PROG := $(shell command -v coverage 2> /dev/null)
PEP8_PROG := $(shell command -v pep8 2> /dev/null)
AUTOPEP8_PROG := $(shell command -v autopep8 2> /dev/null)
PYFLAKES_PROG := $(shell command -v pyflakes 2> /dev/null)
FLAKE8_PROG := $(shell command -v flake8 2> /dev/null)

# run all the unit tests
test:
	@python2.7 -m unittest discover tests

coverage:
ifndef COV_PROG
	$(error "coverage is not available please see: "\
		"https://coverage.readthedocs.io/en/coverage-4.2/install.html")
endif
	@coverage run --source=opentimelineio -m unittest discover tests
	@coverage report -m

test3.5:
	@python3.5 -m unittest discover tests

# run all the unit tests, stopping at the first failure
test_first_fail:
	@python2.7 -m unittest discover tests --failfast

# remove pyc files
clean:
	rm */*.pyc */*/*.pyc

# conform all files to pep8 -- WILL CHANGE FILES IN PLACE
autopep8:
ifndef AUTOPEP8_PROG
	$(error "autopep8 is not available please see: "\
		"https://pypi.python.org/pypi/autopep8#installation")
endif
	find . -name "*.py" | xargs autopep8 --aggressive --in-place -r

# run the codebase through a linter
lint:
ifndef PEP8_PROG
	$(error "pep8 is not available please see: "\
		"https://pypi.python.org/pypi/pep8#installation")
endif
ifndef PYFLAKES_PROG
	$(error "pyflakes is not available please see: "\
		"https://pypi.python.org/pypi/pyflakes#installation")
endif
ifndef FLAKE8_PROG
	$(error "flake8 is not available please see: "\
		"http://flake8.pycqa.org/en/latest/index.html#installation")
endif
	@flake8 opentimelineio bin examples tests

# generate documentation in html
doc-html:
	@make -C doc html | sed 's#build/#doc/build/#g'
