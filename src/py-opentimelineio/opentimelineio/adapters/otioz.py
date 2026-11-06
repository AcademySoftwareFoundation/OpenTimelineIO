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
from . import otio_json

import os
from .bundle_policy import media_reference_policy


def read_from_file(
    filepath,
    # if provided, will extract contents of zip to this directory
    extract_to_directory=None,
):
    options = _otio.bundle.ReadOptions()
    if extract_to_directory is not None:
        options.extract_path = extract_to_directory
    return _otio.bundle.read_otioz(filepath, options)


def write_to_file(
    input_otio,
    filepath,
    relative_media_base_dir=None,
    # see documentation in bundle. for more information on the media_policy
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

    _otio.bundle.write_otioz(input_otio, filepath, options)
    return
