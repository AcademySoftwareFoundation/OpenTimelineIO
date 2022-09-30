# Environment Variables

This document describes the environment variables that can be used to configure
various aspects of OTIO.

## Plugin Configuration

These variables must be set _before_ the OpenTimelineIO python library is imported.  They only impact the python library.  The C++ library has no environment variables.

- `OTIO_PLUGIN_MANIFEST_PATH`: a ":" separated string with paths to .manifest.json files that contain OTIO plugin manifests.  See: [Tutorial on how to write an adapter plugin](write-an-adapter).
- `OTIO_DEFAULT_MEDIA_LINKER`: the name of the default media linker to use after reading a file, if "" then no media linker is automatically invoked.
- `OTIO_DISABLE_PKG_RESOURCE_PLUGINS`: By default, OTIO will use the pkg_resource entry_points mechanism to discover plugins that have been installed into the current python environment.  pkg_resources, however, can be slow in certain cases, so for users who wish to disable this behavior, this variable can be set to 1.
- `OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL`: if no downgrade arguments are passed to `write_to_file`/`write_to_string`, use the downgrade manifest specified by the family/label combination in the variable.  Variable is of the form FAMILY:LABEL.  Only one tuple of FAMILY:LABEL may be specified.

## Unit tests

These variables only impact unit tests.

- `OTIO_DISABLE_SHELLOUT_TESTS`: When running the unit tests, skip the console tests that run the otiocat program and check output through the shell.  This is desirable in environments where running the commandline tests is not meaningful or problematic.  Does not disable the tests that run through python calling mechanisms.
- `OTIO_DISABLE_SERIALIZED_SCHEMA_TEST`: Skip the unit tests that generate documentation and compare the current state of the schema against the stored one. Useful if the documentation is not available from the test directory.
