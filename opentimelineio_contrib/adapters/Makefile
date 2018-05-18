# Makefile for the contrib area

export PYTHONPATH:=../../
TEST_ARGS=
COV_PROG := $(shell command -v coverage 2> /dev/null)

ifeq ($(VERBOSE), 1)
	TEST_ARGS:=-v
endif


test:
	@python -m unittest discover tests $(TEST_ARGS)

coverage:
ifndef COV_PROG
	$(error "coverage is not available please see: "\
		"https://coverage.readthedocs.io/en/coverage-4.2/install.html")
endif
	@${COV_PROG} run -m unittest discover tests
	@${COV_PROG} report -m


