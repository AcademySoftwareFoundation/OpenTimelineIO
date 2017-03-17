

export PYTHONPATH:=../../
export OTIO_PLUGIN_MANIFEST_PATH:=contrib_adapters.plugin_manifest.json
TEST_ARGS=

ifeq ($(VERBOSE), 1)
	TEST_ARGS:=-v
endif


test:
	@python -m unittest discover tests $(TEST_ARGS)

test3.5:
	@python3.5 -m unittest discover tests $(TEST_ARGS)
