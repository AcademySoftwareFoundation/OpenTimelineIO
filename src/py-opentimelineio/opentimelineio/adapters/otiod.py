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
from . import otio_json

import os
from .bundle_policy import media_reference_policy


def read_from_file(
    filepath,
    # convert the media_reference paths to absolute paths
    absolute_media_reference_paths=False,
):
    options = _otio.bundle.ReadOptions()
    options.absolute_media_reference_paths = absolute_media_reference_paths
    return _otio.bundle.read_otiod(filepath, options)


def write_to_file(
    input_otio,
    filepath,
    relative_media_base_dir=None,
    # see documentation bundle.h for more information on the media_policy
    media_policy=_otio.bundle.MediaReferencePolicy.error_if_not_file,
    dryrun=False,
    # schema versions to write content.otio at, see otio_json.write_to_file
    target_schema_versions=None,
):
    if (
        target_schema_versions is None
        and otio_json._DEFAULT_VERSION_ENVVAR in os.environ
    ):
        target_schema_versions = otio_json._fetch_downgrade_map_from_env()

    options = _otio.bundle.WriteOptions()
    options.relative_media_base_dir = relative_media_base_dir
    options.policy = media_reference_policy(media_policy)
    options.target_schema_versions = target_schema_versions

    if dryrun:
        return _otio.bundle.dry_run(input_otio, options)

    _otio.bundle.write_otiod(input_otio, filepath, options)
    return
