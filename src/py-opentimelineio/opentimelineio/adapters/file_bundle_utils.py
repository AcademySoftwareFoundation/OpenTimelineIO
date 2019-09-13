#
# Copyright 2019 Pixar Animation Studios
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

"""Common utilities used by the file bundle adapters (otiod and otioz)."""

import os
import copy


from .. import (
    exceptions,
    schema,
)


try:
    # Python 2.7
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse


BUNDLE_PLAYLIST_PATH = "content.otio"
BUNDLE_DIR_NAME = "media"


class NotAFileOnDisk(exceptions.OTIOError):
    pass


class MediaReferencePolicy:
    ErrorIfNotFile = "ErrorIfNotFile"
    MissingIfNotFile = "MissingIfNotFile"
    AllMissing = "AllMissing"


def reference_cloned_and_missing(orig_mr, reason_missing):
    """Replace orig_mr with a missing reference with the same metadata.

    Also adds original_target_url and missing_reference_because fields.
    """

    orig_mr = copy.deepcopy(orig_mr)
    media_reference = schema.MissingReference()
    media_reference.__dict__ = orig_mr.__dict__
    media_reference.metadata['missing_reference_because'] = reason_missing
    media_reference.metadata['original_target_url'] = orig_mr.target_url

    return media_reference


def _file_bundle_manifest(
    input_otio,
    filepath,
    media_policy,
    adapter_name
):
    """Compute a list of relevant media files that need to be bundled and do
    error checking.
    """

    if os.path.exists(filepath):
        raise exceptions.OTIOError("File already exists: {}".format(filepath))

    referenced_files = set()

    for cl in input_otio.each_clip():
        try:
            target_url = cl.media_reference.target_url
        except AttributeError:
            continue

        parsed_url = urlparse.urlparse(target_url)

        if not parsed_url.scheme == "file":
            if media_policy is MediaReferencePolicy.ErrorIfNotFile:
                raise NotAFileOnDisk(
                    "The {} adapter only works with media reference"
                    " target_url attributes that begin with 'file:'.  Got a "
                    "target_url of:  '{}'".format(adapter_name, target_url)
                )
            if media_policy is MediaReferencePolicy.MissingIfNotFile:
                cl.media_reference = reference_cloned_and_missing(
                    cl.media_reference,
                    "target_url is not a file scheme url (start with url:)"
                )
                continue

        target_file = parsed_url.path

        # if the full path is in the referenced path list.
        if target_file in referenced_files:
            continue

        if not os.path.exists(target_file) or not os.path.isfile(target_file):
            if media_policy is MediaReferencePolicy.ErrorIfNotFile:
                raise NotAFileOnDisk(target_file)
            if media_policy is MediaReferencePolicy.MissingIfNotFile:
                cl.media_reference = reference_cloned_and_missing(
                    cl.media_reference,
                    "target_url target is not a file or does not exist"
                )
                continue

        referenced_files.add(target_file)

    # guarantee that all the basenames are unique
    basename_to_source_fn = {}
    for fn in referenced_files:
        new_basename = os.path.basename(fn)
        if new_basename in basename_to_source_fn:
            raise exceptions.OTIOError(
                "Error: the {} adapter requires that the media files have "
                "unique basenames.  File '{}' and '{}' have matching basenames"
                " of: '{}'".format(
                    adapter_name,
                    fn,
                    basename_to_source_fn[new_basename],
                    new_basename
                )
            )
        basename_to_source_fn[new_basename] = fn

    return referenced_files
