# Makefile for the contrib area

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
	@${COV_PROG} run --rcfile=../../../setup.cfg -p -m unittest discover tests 

coverage-report: coverage
	@${COV_PROG} report -m

clean:
ifdef COV_PROG
	@${COV_PROG} erase
endif

