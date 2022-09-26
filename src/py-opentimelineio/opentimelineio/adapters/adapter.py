# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Implementation of the OTIO internal `Adapter` system.

For information on writing adapters, please consult:
https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html # noqa
"""

import inspect
import collections
import copy

from .. import (
    core,
    plugins,
    media_linker,
    hooks,
)


try:
    # Python 3.0+
    getfullargspec = inspect.getfullargspec
except AttributeError:
    getfullargspec = inspect.getargspec


@core.register_type
class Adapter(plugins.PythonPlugin):
    """Adapters convert between OTIO and other formats.

    Note that this class is not subclassed by adapters. Rather, an adapter is
    a python module that implements at least one of the following functions:

    .. code-block:: python

        write_to_string(input_otio)
        write_to_file(input_otio, filepath) (optionally inferred)
        read_from_string(input_str)
        read_from_file(filepath) (optionally inferred)

    ...as well as a small json file that advertises the features of the adapter
    to OTIO.  This class serves as the wrapper around these modules internal
    to OTIO.  You should not need to extend this class to create new adapters
    for OTIO.

    For more information: https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html. # noqa
    """
    _serializable_label = "Adapter.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
        suffixes=None
    ):
        plugins.PythonPlugin.__init__(
            self,
            name,
            execution_scope,
            filepath
        )

        self.suffixes = suffixes or []

    suffixes = core.serializable_field(
        "suffixes",
        type([]),
        doc="File suffixes associated with this adapter."
    )

    def has_feature(self, feature_string):
        """
        return true if adapter supports feature_string, which must be a key
        of the _FEATURE_MAP dictionary.

        Will trigger a call to :meth:`.PythonPlugin.module`, which imports the plugin.
        """

        if feature_string.lower() not in _FEATURE_MAP:
            return False

        search_strs = _FEATURE_MAP[feature_string]

        try:
            return any(hasattr(self.module(), s) for s in search_strs)
        except ImportError:
            # @TODO: should issue a warning that the plugin was not importable?
            return False

    def read_from_file(
        self,
        filepath,
        media_linker_name=media_linker.MediaLinkingPolicy.ForceDefaultLinker,
        media_linker_argument_map=None,
        hook_function_argument_map=None,
        **adapter_argument_map
    ):
        """Execute the read_from_file function on this adapter.

        If read_from_string exists, but not read_from_file, execute that with
        a trivial file object wrapper.
        """

        media_linker_argument_map = copy.deepcopy(
            media_linker_argument_map or {}
        )

        result = None

        if (
            not self.has_feature("read_from_file") and
            self.has_feature("read_from_string")
        ):
            with open(filepath) as fo:
                contents = fo.read()
            result = self._execute_function(
                "read_from_string",
                input_str=contents,
                **adapter_argument_map
            )
        else:
            result = self._execute_function(
                "read_from_file",
                filepath=filepath,
                **adapter_argument_map
            )

        hook_function_argument_map = copy.deepcopy(
            hook_function_argument_map or {}
        )
        hook_function_argument_map['adapter_arguments'] = copy.deepcopy(
            adapter_argument_map
        )
        hook_function_argument_map['media_linker_argument_map'] = (
            media_linker_argument_map
        )
        result = hooks.run(
            "post_adapter_read",
            result,
            extra_args=hook_function_argument_map
        )

        if media_linker_name and (
            media_linker_name != media_linker.MediaLinkingPolicy.DoNotLinkMedia
        ):
            _with_linked_media_references(
                result,
                media_linker_name,
                media_linker_argument_map
            )

        result = hooks.run(
            "post_media_linker",
            result,
            extra_args=media_linker_argument_map
        )

        return result

    def write_to_file(
        self,
        input_otio,
        filepath,
        hook_function_argument_map=None,
        **adapter_argument_map
    ):
        """Execute the write_to_file function on this adapter.

        If write_to_string exists, but not write_to_file, execute that with
        a trivial file object wrapper.
        """

        hook_function_argument_map = copy.deepcopy(
            hook_function_argument_map or {}
        )
        hook_function_argument_map['adapter_arguments'] = copy.deepcopy(
            adapter_argument_map
        )

        # Store file path for use in hooks
        hook_function_argument_map['_filepath'] = filepath

        input_otio = hooks.run("pre_adapter_write", input_otio,
                               extra_args=hook_function_argument_map)
        if (
            not self.has_feature("write_to_file") and
            self.has_feature("write_to_string")
        ):
            result = self.write_to_string(input_otio, **adapter_argument_map)
            with open(filepath, 'w') as fo:
                fo.write(result)
            result = filepath

        else:
            result = self._execute_function(
                "write_to_file",
                input_otio=input_otio,
                filepath=filepath,
                **adapter_argument_map
            )

        hooks.run(
            "post_adapter_write",
            input_otio,
            extra_args=hook_function_argument_map
        )

        return result

    def read_from_string(
        self,
        input_str,
        media_linker_name=media_linker.MediaLinkingPolicy.ForceDefaultLinker,
        media_linker_argument_map=None,
        hook_function_argument_map=None,
        **adapter_argument_map
    ):
        """Call the read_from_string function on this adapter."""

        result = self._execute_function(
            "read_from_string",
            input_str=input_str,
            **adapter_argument_map
        )

        hook_function_argument_map = copy.deepcopy(
            hook_function_argument_map or {}
        )
        hook_function_argument_map['adapter_arguments'] = copy.deepcopy(
            adapter_argument_map
        )
        hook_function_argument_map['media_linker_argument_map'] = copy.deepcopy(
            media_linker_argument_map
        )

        result = hooks.run(
            "post_adapter_read",
            result,
            extra_args=hook_function_argument_map
        )

        if media_linker_name and (
            media_linker_name != media_linker.MediaLinkingPolicy.DoNotLinkMedia
        ):
            _with_linked_media_references(
                result,
                media_linker_name,
                media_linker_argument_map
            )

        # @TODO: Should this run *ONLY* if the media linker ran?
        result = hooks.run(
            "post_media_linker",
            result,
            extra_args=hook_function_argument_map
        )

        return result

    def write_to_string(
        self,
        input_otio,
        hook_function_argument_map=None,
        **adapter_argument_map
    ):
        """Call the write_to_string function on this adapter."""

        hook_function_argument_map = copy.deepcopy(
            hook_function_argument_map or {}
        )
        hook_function_argument_map['adapter_arguments'] = copy.deepcopy(
            adapter_argument_map
        )
        input_otio = hooks.run(
            "pre_adapter_write",
            input_otio,
            extra_args=hook_function_argument_map
        )

        return self._execute_function(
            "write_to_string",
            input_otio=input_otio,
            **adapter_argument_map
        )

    def __str__(self):
        return (
            "Adapter("
            "{}, "
            "{}, "
            "{}, "
            "{}"
            ")".format(
                repr(self.name),
                repr(self.execution_scope),
                repr(self.filepath),
                repr(self.suffixes),
            )
        )

    def __repr__(self):
        return (
            "otio.adapter.Adapter("
            "name={}, "
            "execution_scope={}, "
            "filepath={}, "
            "suffixes={}"
            ")".format(
                repr(self.name),
                repr(self.execution_scope),
                repr(self.filepath),
                repr(self.suffixes),
            )
        )

    def plugin_info_map(self):
        """Adds extra adapter-specific information to call to the parent fn."""

        result = super().plugin_info_map()

        features = collections.OrderedDict()
        result["supported features"] = features

        for feature in sorted(_FEATURE_MAP.keys()):
            if feature in ["read", "write"]:
                continue
            if self.has_feature(feature):
                features[feature] = collections.OrderedDict()

                # find the function
                args = []
                for fn_name in _FEATURE_MAP[feature]:
                    if hasattr(self.module(), fn_name):
                        fn = getattr(self.module(), fn_name)
                        args = getfullargspec(fn)
                        docs = inspect.getdoc(fn)
                        break

                if args:
                    features[feature]["args"] = args.args
                    features[feature]["doc"] = docs

        return result


def _with_linked_media_references(
    read_otio,
    media_linker_name,
    media_linker_argument_map
):
    """Link media references in the read_otio if possible.

    Makes changes in place and returns the read_otio structure back.
    """

    if not read_otio or not media_linker.from_name(media_linker_name):
        return read_otio

    # not every object the adapter reads has an "each_clip" method, so this
    # skips objects without one.
    clpfn = getattr(read_otio, "each_clip", None)
    if clpfn is None:
        return read_otio

    for cl in read_otio.each_clip():
        new_mr = media_linker.linked_media_reference(
            cl,
            media_linker_name,
            # @TODO: should any context get wired in at this point?
            media_linker_argument_map
        )
        if new_mr is not None:
            cl.media_reference = new_mr

    return read_otio


# map of attr to look for vs feature name in the adapter plugin
_FEATURE_MAP = {
    'read_from_file': ['read_from_file'],
    'read_from_string': ['read_from_string'],
    'read': ['read_from_file', 'read_from_string'],
    'write_to_file': ['write_to_file'],
    'write_to_string': ['write_to_string'],
    'write': ['write_to_file', 'write_to_string']
}
