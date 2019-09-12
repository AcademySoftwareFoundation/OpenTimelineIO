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

"""OTIOD adapter - bundles otio files linked to local media in a directory

Takes as input an OTIO file that has media references which are all
ExternalReferences with target_urls to files with unique basenames that
accessible through the file system and bundles those files and the otio file
into a single directory named with a suffix of .otiod.
"""

import os
import copy
import shutil

from . import (
    file_bundle_utils as utils,
    otio_json,
)

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


def read_from_file(filepath, absolute_media_reference_paths=False):
    result = otio_json.read_from_file(
        os.path.join(filepath, utils.BUNDLE_PLAYLIST_PATH)
    )

    if not absolute_media_reference_paths:
        return result

    for cl in result.each_clip():
        try:
            source_fpath = cl.media_reference.target_url
        except AttributeError:
            continue

        rel_path = urlparse.urlparse(source_fpath).path
        new_fpath = "file:{}".format(os.path.join(filepath, rel_path))

        cl.media_reference.target_url = new_fpath

    return result


def write_to_file(
    input_otio,
    filepath,
    media_policy=utils.MediaReferencePolicy.ErrorIfNotFile,
    dryrun=False
):
    # make sure the incoming OTIO isn't edited
    input_otio = copy.deepcopy(input_otio)

    manifest = utils._file_bundle_manifest(
        input_otio,
        filepath,
        media_policy,
        "OTIOD"
    )

    # dryrun reports the total size of files
    if dryrun:
        fsize = 0
        for fn in manifest:
            fsize += os.path.getsize(fn)
        return fsize

    fmapping = {}

    # gather the files up in the staging_dir
    for fn in manifest:
        target = os.path.join(
            filepath,
            utils.BUNDLE_DIR_NAME,
            os.path.basename(fn)
        )
        fmapping[fn] = target

    # so we don't edit the incoming file
    input_otio = copy.deepcopy(input_otio)

    # update the media reference
    for cl in input_otio.each_clip():
        if media_policy == utils.MediaReferencePolicy.AllMissing:
            cl.media_reference = schema.MissingReference()
            continue

        try:
            source_fpath = cl.media_reference.target_url
        except AttributeError:
            continue

        basename = os.path.basename(urlparse.urlparse(source_fpath).path)
        newpath = os.path.join("media", basename)

        cl.media_reference.target_url = "file:{}".format(newpath)

    if not os.path.exists(os.path.dirname(filepath)):
        raise exceptions.OTIOError(
            "Error: directory '{}' does not exist, cannot create '{}'".format(
                os.path.dirname(filepath),
                filepath
            )
        )
    os.mkdir(filepath)

    # write the otioz file to the temp directory
    otio_json.write_to_file(
        input_otio,
        os.path.join(filepath, utils.BUNDLE_PLAYLIST_PATH)
    )

    # write the media files
    os.mkdir(os.path.join(filepath, utils.BUNDLE_DIR_NAME))
    for src, dst in fmapping.items():
        shutil.copyfile(src, dst)

    return
