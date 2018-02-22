# Makefile for the contrib area

export PYTHONPATH:=../../
TEST_ARGS=

ifeq ($(VERBOSE), 1)
	TEST_ARGS:=-v
endif


test:
	@python -m unittest discover tests $(TEST_ARGS)
