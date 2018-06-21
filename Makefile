.PHONY: coverage test test_first_fail clean autopep8 lint doc-html \
	python-version

# Special definition to handle Make from stripping newlines
define newline


endef

# Color highlighting for the shell
ccred = $(shell echo "\033[0;31m")
ccgreen = $(shell echo "\033[0;32m")
ccblue = $(shell echo "\033[0;34m")
ccend = $(shell echo "\033[0m")

# Helpful link to install development dependencies declared in setup.py
define dev_deps_message
$(ccred)You can install this and other development dependencies with$(newline)$(ccend)\
$(ccblue)	pip install -e .[dev]$(newline)$(ccend)
endef

COV_PROG := $(shell command -v coverage 2> /dev/null)
PEP8_PROG := $(shell command -v pep8 2> /dev/null)
PYFLAKES_PROG := $(shell command -v pyflakes 2> /dev/null)
FLAKE8_PROG := $(shell command -v flake8 2> /dev/null)
# AUTOPEP8_PROG := $(shell command -v autopep8 2> /dev/null)
TEST_ARGS=

ifeq ($(VERBOSE), 1)
	TEST_ARGS:=-v
endif

# Clear the environment of a preset media linker
OTIO_DEFAULT_MEDIA_LINKER =

# run all the unit tests
test: test-core test-contrib

test-core: python-version
	@echo "$(ccgreen)Running Core tests...$(ccend)"
	@python -m unittest discover tests $(TEST_ARGS)

test-contrib: python-version
	@echo "$(ccgreen)Running Contrib tests...$(ccend)"
	@make -C opentimelineio_contrib/adapters test VERBOSE=$(VERBOSE)

python-version:
	@python --version

coverage: coverage-core coverage-contrib

coverage-core: python-version
ifndef COV_PROG
	$(error $(newline)$(ccred) Coverage is not available please see:$(newline)$(ccend)\
	$(ccblue)	https://coverage.readthedocs.io/en/coverage-4.2/install.html $(newline)$(ccend)\
	$(dev_deps_message))
endif
	@${COV_PROG} run --source=opentimelineio -m unittest discover tests
	@${COV_PROG} report -m

coverage-contrib: python-version
	@make -C opentimelineio_contrib/adapters coverage VERBOSE=$(VERBOSE)

# run all the unit tests, stopping at the first failure
test_first_fail: python-version
	@python -m unittest discover tests --failfast

# remove pyc files
clean:
	rm */*.pyc */*/*.pyc

# conform all files to pep8 -- WILL CHANGE FILES IN PLACE
# autopep8:
# ifndef AUTOPEP8_PROG
# 	$(error "autopep8 is not available please see: "\
# 		"https://pypi.python.org/pypi/autopep8#installation")
# endif
# 	find . -name "*.py" | xargs ${AUTOPEP8_PROG} --aggressive --in-place -r

# run the codebase through flake8.  pep8 and pyflakes are called by flake8.
lint:
ifndef PEP8_PROG
	$(error $(newline)$(ccred)pep8 is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	https://pypi.python.org/pypi/pep8#installation$(newline)$(ccend)\
	$(dev_deps_message))
endif
ifndef PYFLAKES_PROG
	$(error $(newline)$(ccred)pyflakes is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	https://pypi.python.org/pypi/pyflakes#installation$(newline)$(ccend)\
	$(dev_deps_message))
endif
ifndef FLAKE8_PROG
	$(error $(newline)$(ccred)flake8 is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	http://flake8.pycqa.org/en/latest/index.html#installation$(newline)$(ccend)\
	$(dev_deps_message))
endif
	@python -m flake8 --exclude build


# generate documentation in html
doc-html:
	@make -C doc html | sed 's#build/#doc/build/#g'
