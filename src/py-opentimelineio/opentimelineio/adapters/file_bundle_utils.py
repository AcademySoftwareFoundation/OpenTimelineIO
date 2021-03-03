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


# versioning
BUNDLE_VERSION = "1.0.0"
BUNDLE_VERSION_FILE = "version.txt"

# other variables
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


def _prepped_otio_for_bundle_and_manifest(
    input_otio,    # otio to process
    media_policy,  # what to do with media references
    adapter_name,  # just for error messages
):
    """ Create a new OTIO based on input_otio that has had media references
    replaced according to the media_policy.  Return that new OTIO and a
    manifest of all the unique file paths (not URLs) to be used in the bundle.
    Media references in the OTIO will all point at paths in the manifest.

    The otio[dz] adapters use this function to do further relinking and build
    their bundles.

    This is considered an internal API.
    """

    # make sure the incoming OTIO isn't edited
    result_otio = copy.deepcopy(input_otio)

    referenced_files = set()
    invalid_files = set()

    # result_otio is manipulated in place
    for cl in result_otio.each_clip():
        try:
            target_url = cl.media_reference.target_url
        except AttributeError:
            continue

        parsed_url = urlparse.urlparse(target_url)

        # ensure that the urlscheme is either file or ""
        # file means "absolute path"
        # none is interpreted as a relative path, relative to cwd
        if parsed_url.scheme not in ("file", ""):
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

        # if the file hasn't already been checked
        if (
            target_file not in referenced_files
            and target_file not in invalid_files
            and (
                not os.path.exists(target_file)
                or not os.path.isfile(target_file)
            )
        ):
            invalid_files.add(target_file)

        if target_file in invalid_files:
            if media_policy is MediaReferencePolicy.ErrorIfNotFile:
                raise NotAFileOnDisk(target_file)
            if media_policy is MediaReferencePolicy.MissingIfNotFile:
                cl.media_reference = reference_cloned_and_missing(
                    cl.media_reference,
                    "target_url target is not a file or does not exist"
                )
                continue

        # make sure that the reference matches what goes into the manifest
        # the adapters will write the final result into the outgoing OTIO
        cl.media_reference.target_url = target_file

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

    return result_otio, referenced_files

def _file_bundle_manifest(
    input_otio,
    # only used for error checking
    dest_path,
    media_policy,
    adapter_name
):
    """
    error checking.

    # 1 - ensure that the destination path doesn't already exist
    # 2 - for each media reference
    #      - apply the media refernece policy IN PLACE
    #      - do error checking on missing files, etc
    # 3 - build a list of referenced files
    """

    referenced_files = set()

    for cl in input_otio.each_clip():
        try:
            target_url = cl.media_reference.target_url
        except AttributeError:
            continue

        parsed_url = urlparse.urlparse(target_url)

        # ensure that the urlscheme is either file or "" (which is interpret as
        # file)
        if parsed_url.scheme not in ("file", ""):
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

        final = file_url_of(target_file)
        referenced_files.add(final)

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


def file_url_of(fpath):
    """convert a filesystem path to an url in a portable way"""

    # scheme is "file" for absolute paths, else ""
    scheme = "file" if os.path.isabs(fpath) else ""

    return urlparse.urlunparse(
        urlparse.ParseResult(
            scheme=scheme,
            path=fpath,
            netloc="",
            params="",
            query="",
            fragment=""
        )
    )
