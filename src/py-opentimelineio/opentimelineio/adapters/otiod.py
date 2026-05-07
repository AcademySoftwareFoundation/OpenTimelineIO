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
    return _otio.bundle.read_otiod(filepath, options)


def write_to_file(
    input_otio,
    filepath,
    relative_media_path=None,
    # see documentation bundle.h for more information on the media_policy
    media_policy=_otio.bundle.MediaReferencePolicy.error_if_not_file,
    dryrun=False
):
    options = _otio.bundle.WriteOptions()
    options.relative_media_path = relative_media_path
    options.media_policy = media_policy

    if dryrun:
        return _otio.bundle.dry_run(input_otio, options)

    _otio.bundle.write_otiod(input_otio, filepath, options)
    return
