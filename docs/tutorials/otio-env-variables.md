# Environment Variables

This document describes the environment variables that can be used to configure
various aspects of OTIO.

## Plugin Configuration

These variables must be set _before_ the OpenTimelineIO python library is imported.

- `OTIO_PLUGIN_MANIFEST_PATH`: a ":" separated string with paths to .manifest.json files that contain OTIO plugin manifests.  See: <a href="write-an-adapter.html" target="_blank">Tutorial on how to write an adapter plugin</a>.
- `OTIO_DEFAULT_MEDIA_LINKER`: the name of the default media linker to use after reading a file, if "" then no media linker is automatically invoked.
- `OTIO_DISABLE_PKG_RESOURCE_PLUGINS`: By default, OTIO will use the pkg_resource entry_points mechanism to discover plugins that have been installed into the current python environment.  pkg_resources, however, can be slow in certain cases, so for users who wish to disable this behavior, this variable can be set to 1.

## Unit tests

These variables only impact unit tests.

- `OTIO_DISABLE_SHELLOUT_TESTS`: When running the unit tests, skip the console tests that run the otiocat program and check output through the shell.  This is desirable in environments where running the commandline tests is not meaningful or problematic.  Does not disable the tests that run through python calling mechanisms.
- `OTIO_DISABLE_SERIALIZED_SCHEMA_TEST`: Skip the unit tests that generate documentation and compare the current state of the schema against the stored one. Useful if the documentation is not available from the test directory.
