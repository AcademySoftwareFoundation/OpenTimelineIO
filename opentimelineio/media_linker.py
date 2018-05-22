#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

""" MediaLinker plugins fire after an adapter has read a file in oder to
produce MediaReferences that point at valid, site specific media.

They expose a "link_media_reference" function with the signature:
link_media_reference :: otio.schema.Clip -> otio.core.MediaReference

or:
    def linked_media_reference(from_clip):
        result = otio.core.MediaReference() # whichever subclass
        # do stuff
        return result

To get context information, they can inspect the metadata on the clip and on
the media reference.  The .parent() method can be used to find the containing
track if metadata is stored there.

Please raise an instance (or child instance) of
otio.exceptions.CannotLinkMediaError() if there is a problem linking the media.

For example:
    for clip in timeline.each_clip():
        try:
            new_mr = otio.media_linker.linked_media_reference(clip)
            clip.media_reference = new_mr
        except otio.exceptions.CannotLinkMediaError:
            # or report the error
            pass
"""

import os

from . import (
    exceptions,
    plugins,
    core,
)


# Enum describing different media linker policies
class MediaLinkingPolicy:
    DoNotLinkMedia = "__do_not_link_media"
    ForceDefaultLinker = "__default"


# @TODO: wrap this up in the plugin system somehow?  automatically generate?
def available_media_linker_names():
    """Return a string list of the available media linker plugins."""

    return [str(adp.name) for adp in plugins.ActiveManifest().media_linkers]


def from_name(name):
    """Fetch the media linker object by the name of the adapter directly."""

    if name == MediaLinkingPolicy.ForceDefaultLinker or not name:
        name = os.environ.get("OTIO_DEFAULT_MEDIA_LINKER", None)

    if not name:
        return None

    # @TODO: make this handle the enums
    try:
        return plugins.ActiveManifest().from_name(
            name,
            kind_list="media_linkers"
        )
    except exceptions.NotSupportedError:
        raise exceptions.NotSupportedError(
            "media linker not supported: {}, available: {}".format(
                name,
                available_media_linker_names()
            )
        )


def default_media_linker():
    try:
        return os.environ['OTIO_DEFAULT_MEDIA_LINKER']
    except KeyError:
        raise exceptions.NoDefaultMediaLinkerError(
            "No default Media Linker set in $OTIO_DEFAULT_MEDIA_LINKER"
        )


def linked_media_reference(
    target_clip,
    media_linker_name=MediaLinkingPolicy.ForceDefaultLinker,
    media_linker_argument_map=None
):
    media_linker = from_name(media_linker_name)

    if not media_linker:
        return target_clip

    # @TODO: connect this argument map up to the function call through to the
    #        real linker
    if not media_linker_argument_map:
        media_linker_argument_map = {}

    return media_linker.link_media_reference(
        target_clip,
        media_linker_argument_map
    )


@core.register_type
class MediaLinker(plugins.PythonPlugin):
    _serializable_label = "MediaLinker.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
    ):
        plugins.PythonPlugin.__init__(self, name, execution_scope, filepath)

    def link_media_reference(self, in_clip, media_linker_argument_map=None):
        media_linker_argument_map = media_linker_argument_map or {}

        return self._execute_function(
            "link_media_reference",
            in_clip=in_clip,
            media_linker_argument_map=media_linker_argument_map
        )

    def __str__(self):
        return "MediaLinker({}, {}, {})".format(
            repr(self.name),
            repr(self.execution_scope),
            repr(self.filepath)
        )

    def __repr__(self):
        return (
            "otio.media_linker.MediaLinker("
            "name={}, "
            "execution_scope={}, "
            "filepath={}"
            ")".format(
                repr(self.name),
                repr(self.execution_scope),
                repr(self.filepath)
            )
        )
