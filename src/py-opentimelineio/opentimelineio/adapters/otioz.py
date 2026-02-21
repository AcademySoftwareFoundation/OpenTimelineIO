# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OTIOZ adapter - bundles otio files linked to local media

Takes as input an OTIO file that has media references which are all
ExternalReferences with target_urls to files with unique basenames that are
accessible through the file system and bundles those files and the otio file
into a single zip file with the suffix .otioz.  Can error out if files aren't
locally referenced or provide missing references

Can also extract the content.otio file from an otioz bundle for processing.

Note that OTIOZ files _always_ use the unix style path separator ('/'). This
ensures that regardless of which platform a bundle was created on, it can be
read on unix and windows platforms.
"""

from .. import (
    _otio
)


def read_from_file(
    filepath,
    # if provided, will extract contents of zip to this directory
    extract_to_directory=None,
):
    options = _otio.bundle.OtiozReadOptions()
    if extract_to_directory is not None:
        options.extract_path = extract_to_directory
    return _otio.bundle.from_otioz(filepath, options)


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

    _otio.bundle.to_otioz(input_otio, filepath, options)
    return
