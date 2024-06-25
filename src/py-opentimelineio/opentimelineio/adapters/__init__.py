# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Expose the adapter interface to developers.

To read from an existing representation, use the read_from_string and
read_from_file functions.  To query the list of adapters, use the
available_adapter_names function.

The otio_json adapter is provided as a the canonical, lossless, serialization
of the in-memory otio schema.  Other adapters are to varying degrees lossy.
For more information, consult the documentation in the individual adapter
modules.
"""

import os
import itertools
import pathlib

from .. import (
    exceptions,
    plugins,
    media_linker
)

from .adapter import Adapter  # noqa

# OTIO Json, OTIOZ and OTIOD adapters are always available
from . import (  # noqa: F401
    otio_json,  # core JSON adapter
    file_bundle_utils,  # utilities for working with OTIO file bundles
)

__all__ = [
    'Adapter',
    'otio_json',
    'file_bundle_utils',
    'suffixes_with_defined_adapters',
    'available_adapter_names',
    'from_filepath',
    'from_name',
    'read_from_file',
    'read_from_string',
    'write_to_file',
    'write_to_string'
]


def suffixes_with_defined_adapters(read=False, write=False):
    """Return a set of all the suffixes that have adapters defined for them."""

    if not read and not write:
        read = True
        write = True

    positive_adapters = []
    for adp in plugins.ActiveManifest().adapters:
        if read and adp.has_feature("read"):
            positive_adapters.append(adp)
            continue

        if write and adp.has_feature("write"):
            positive_adapters.append(adp)

    return set(
        itertools.chain.from_iterable(
            adp.suffixes for adp in positive_adapters
        )
    )


def available_adapter_names():
    """Return a string list of the available adapters."""

    return [str(adp.name) for adp in plugins.ActiveManifest().adapters]


def _from_filepath_or_name(filepath, adapter_name):
    if adapter_name is not None:
        return plugins.ActiveManifest().from_name(adapter_name)
    return from_filepath(filepath)


def from_filepath(filepath):
    """Guess the adapter object to use for a given filepath.

    For example, ``foo.otio`` returns the ``otio_json`` adapter.
    """

    outext = os.path.splitext(filepath)[1][1:]

    try:
        return plugins.ActiveManifest().from_filepath(outext)
    except exceptions.NoKnownAdapterForExtensionError:
        raise exceptions.NoKnownAdapterForExtensionError(
            "No adapter for suffix '{}' on file '{}'".format(
                outext,
                filepath
            )
        )


def from_name(name):
    """Fetch the adapter object by the name of the adapter directly."""

    try:
        return plugins.ActiveManifest().from_name(name)
    except exceptions.NotSupportedError:
        raise exceptions.NotSupportedError(
            "adapter not supported: {}, available: {}".format(
                name,
                available_adapter_names()
            )
        )


def read_from_file(
    filepath,
    adapter_name=None,
    media_linker_name=media_linker.MediaLinkingPolicy.ForceDefaultLinker,
    media_linker_argument_map=None,
    **adapter_argument_map
):
    """Read filepath using adapter_name.

    If adapter_name is None, try and infer the adapter name from the filepath.

    .. code-block:: python
       :caption: Example

        timeline = read_from_file("example_trailer.otio")
        timeline = read_from_file("file_with_no_extension", "cmx_3600")
    """

    # convert pathlib Path objects to simple string
    string_filepath = filepath
    if isinstance(string_filepath, pathlib.PurePath):
        string_filepath = os.fspath(filepath)

    adapter = _from_filepath_or_name(string_filepath, adapter_name)

    return adapter.read_from_file(
        filepath=string_filepath,
        media_linker_name=media_linker_name,
        media_linker_argument_map=media_linker_argument_map,
        **adapter_argument_map
    )


def read_from_string(
    input_str,
    adapter_name='otio_json',
    media_linker_name=media_linker.MediaLinkingPolicy.ForceDefaultLinker,
    media_linker_argument_map=None,
    **adapter_argument_map
):
    """Read a timeline from input_str using adapter_name.

    This is useful if you obtain a timeline from someplace other than the
    filesystem.

    .. code-block:: python
       :caption: Example

        raw_text = urlopen(my_url).read()
        timeline = read_from_string(raw_text, "otio_json")
    """

    adapter = plugins.ActiveManifest().from_name(adapter_name)
    return adapter.read_from_string(
        input_str=input_str,
        media_linker_name=media_linker_name,
        media_linker_argument_map=media_linker_argument_map,
        **adapter_argument_map
    )


def write_to_file(
    input_otio,
    filepath,
    adapter_name=None,
    **adapter_argument_map
):
    """Write input_otio to filepath using adapter_name.

    If adapter_name is None, infer the adapter_name to use based on the
    filepath.

    .. code-block:: python
       :caption: Example

        otio.adapters.write_to_file(my_timeline, "output.otio")
    """

    adapter = _from_filepath_or_name(filepath, adapter_name)

    # convert pathlib Path objects to simple string
    string_filepath = filepath
    if isinstance(string_filepath, pathlib.PurePath):
        string_filepath = os.fspath(filepath)

    return adapter.write_to_file(
        input_otio=input_otio,
        filepath=string_filepath,
        **adapter_argument_map
    )


def write_to_string(
    input_otio,
    adapter_name='otio_json',
    **adapter_argument_map
):
    """Return input_otio written to a string using adapter_name.

    .. code-block:: python
       :caption: Example

        raw_text = otio.adapters.write_to_string(my_timeline, "otio_json")
    """

    adapter = plugins.ActiveManifest().from_name(adapter_name)
    return adapter.write_to_string(
        input_otio=input_otio,
        **adapter_argument_map
    )
