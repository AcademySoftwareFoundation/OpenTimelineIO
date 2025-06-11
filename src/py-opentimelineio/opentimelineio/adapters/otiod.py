# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OTIOD adapter - bundles otio files linked to local media in a directory

Takes as input an OTIO file that has media references which are all
ExternalReferences with target_urls to files with unique basenames that are
accessible through the file system and bundles those files and the otio file
into a single directory named with a suffix of .otiod.
"""

from .. import (
    _otio
)


def read_from_file(
    filepath,
    # convert the media_reference paths to absolute paths
    absolute_media_reference_paths=False,
):
    options = _otio.bundle.OtiodReadOptions()
    options.absolute_media_reference_paths = absolute_media_reference_paths
    return _otio.bundle.from_otiod(filepath, options)


def write_to_file(
    input_otio,
    filepath,
    # see documentation in bundle.h for more information on the media_policy
    media_policy=_otio.bundle.MediaReferencePolicy.ErrorIfNotFile,
    dryrun=False
):
    options = _otio.bundle.WriteOptions()
    options.media_policy = media_policy

    if dryrun:
        return _otio.bundle.get_media_size(input_otio, options)

    _otio.bundle.to_otiod(input_otio, filepath, options)
    return
