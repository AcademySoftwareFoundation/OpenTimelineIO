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

Takes as input an OTIO file that has media references which are all relative
local paths (ie file:///foo.mov) and bundles those files and the otio file into
a single directory named with a suffix of .otiod.
"""

import os
import copy
import shutil

from . import (
    otioz,
    otio_json,
)

from .. import (
    exceptions,
    schema,
)


def read_from_file(filepath):
    return otio_json.read_from_file(
        os.path.join(filepath, otioz.BUNDLE_PLAYLIST_PATH)
    )


def write_to_file(
    input_otio,
    filepath,
    unreachable_media_policy=otioz.MediaReferencePolicy.ErrorIfNotFile,
    dryrun=False
):
    if os.path.exists(filepath):
        raise exceptions.OTIOError("File already exists: {}".format(filepath))

    referenced_files = set()

    for cl in input_otio.each_clip():
        try:
            target_url = cl.media_reference.target_url
        except AttributeError:
            continue

        if not target_url.startswith("file://"):
            if unreachable_media_policy is otioz.MediaReferencePolicy.ErrorIfNotFile:
                raise otioz.NotAFileOnDisk(
                    "The OTIOZ adapter only works with media reference"
                    " target_url attributes that begin with 'file://'.  Got a "
                    "target_url of:  '{}'".format(target_url)
                )
            if unreachable_media_policy is otioz.MediaReferencePolicy.MissingIfNotFile:
                md = copy.deepcopy(cl.media_reference)
                cl.media_reference = schema.MissingReference(
                    name=md.name,
                    metadata={
                        'OTIOZ': {
                            'original_reference': md,
                            'missing_reference_because': (
                                "target_url does not start with 'file://'"
                            )
                        }
                    }
                )
                continue

        target_file = target_url.split("file://", 1)[1]

        # if the full path is in the referenced path list.
        if target_file in referenced_files:
            continue

        if not os.path.exists(target_file) or not os.path.isfile(target_file):
            if unreachable_media_policy is otioz.MediaReferencePolicy.ErrorIfNotFile:
                raise otioz.NotAFileOnDisk(target_file)
            if unreachable_media_policy is otioz.MediaReferencePolicy.MissingIfNotFile:
                md = copy.deepcopy(cl.media_reference)
                cl.media_reference = schema.MissingReference(
                    name=md.name,
                    metadata={
                        'OTIOZ': {
                            'original_reference': md,
                            'missing_reference_because': (
                                "target_url target is not a file or does not "
                                "exist"
                            )
                        }
                    }
                )
                continue

        referenced_files.add(target_file)

    # guarantee that all the basenames are unique
    basename_to_source_fn = {}
    for fn in referenced_files:
        new_basename = os.path.basename(fn)
        if new_basename in basename_to_source_fn:
            raise exceptions.OTIOError(
                "Error: the OTIOZ adapter requires that the media files have "
                "unique basenames.  File '{}' and '{}' have matching basenames"
                " of: '{}'".format(
                    fn,
                    basename_to_source_fn[new_basename],
                    new_basename
                )
            )
        basename_to_source_fn[new_basename] = fn

    # dryrun reports the total size of files
    if dryrun:
        fsize = 0
        for fn in referenced_files:
            fsize += os.path.getsize(fn)
        return fsize

    fmapping = {}

    # gather the files up in the staging_dir
    for fn in referenced_files:
        target = os.path.join(
            filepath,
            otioz.BUNDLE_DIR_NAME,
            os.path.basename(fn)
        )
        fmapping[fn] = target

    # so we don't edit the incoming file
    input_otio = copy.deepcopy(input_otio)

    # update the media reference
    for cl in input_otio.each_clip():
        try:
            source_fpath = cl.media_reference.target_url
        except AttributeError:
            continue

        cl.media_reference.target_url = "file://{}".format(
            fmapping[source_fpath.split("file://")[1]]
        )

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
        os.path.join(filepath, otioz.BUNDLE_PLAYLIST_PATH)
    )

    # write the media files
    os.mkdir(os.path.join(filepath, otioz.BUNDLE_DIR_NAME))
    for src, dst in fmapping.items():
        shutil.copyfile(src, dst)

    return
