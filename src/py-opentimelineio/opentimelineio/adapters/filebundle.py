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

"""OTIOZ adapter - bundles otio files linked to local media

Takes as input an OTIO file that has media references which are all relative
local paths (ie file:///foo.mov) and bundles those files and the otio file into
a single zip file with the suffix .otioz.  Can error out if files aren't
locally referenced or provide missing references
"""

import os
import copy
import zipfile

from .. import (
    exceptions,
    schema,
)

from . import (
    otio_json
)


class NotAFileOnDisk(exceptions.OTIOError):
    pass


def read_from_file(filepath):
    if not zipfile.is_zipfile(filepath):
        raise exceptions.OTIOError("Not a zipfile: {}".format(filepath))

    internal_playlist_file = "{0}/{0}.otio".format(
        os.path.splitext(os.path.basename(filepath))[0]
    )
    with zipfile.ZipFile(filepath, 'r') as zi:
        result = otio_json.read_from_string(zi.read(internal_playlist_file))

    return result


class MediaReferencePolicy:
    ErrorIfNotFile = 0
    MissingIfNotFile = 1


def write_to_file(
    input_otio,
    filepath,
    unreachable_media_policy=MediaReferencePolicy.ErrorIfNotFile,
    dryrun=False
):
    referenced_files = set()

    for cl in input_otio.each_clip():
        try:
            target_file = cl.media_reference.target_url
        except AttributeError:
            continue

        if target_file in referenced_files:
            continue

        if not os.path.exists(target_file) or not os.path.isfile(target_file):
            if unreachable_media_policy is MediaReferencePolicy.ErrorIfNotFile:
                raise NotAFileOnDisk(target_file)
            if unreachable_media_policy is MediaReferencePolicy.MissingIfNotFile:
                md = copy.deepcopy(cl.media_reference)
                cl.media_reference = schema.MissingReference(
                    name=md.name,
                    metadata={
                        'OTIOZ': {
                            'original_reference': md
                        }
                    }
                )
                continue

        referenced_files.add(target_file)

    # dryrun reports the total size of files
    if dryrun:
        fsize = 0
        for fn in referenced_files:
            fsize += os.path.getsize(fn)
        return fsize

    fmapping = {}

    # strip off the [z] suffix
    otio_basename = os.path.splitext(os.path.basename(filepath))[0]

    # gather the files up in the staging_dir
    for fn in referenced_files:
        target = os.path.join(otio_basename, os.path.basename(fn))
        fmapping[fn] = target

    # update the media references
    for cl in input_otio.each_clip():
        try:
            source_fpath = cl.metadata.target_url
        except AttributeError:
            continue

        cl.metadata.target_url = "file://{}".format(fmapping[source_fpath])

    # write the otioz file to the temp directory
    otio_str = otio_json.write_to_string(input_otio)

    # zip the whole thing up
    if os.path.exists(filepath):
        raise exceptions.OTIOError("File already exists: {}".format(filepath))

    with zipfile.ZipFile(filepath, mode='w') as target:
        # write the media
        for src, dst in fmapping.items():
            target.write(src, dst)

        # write the OTIO
        target.writestr(
            os.path.join(otio_basename, "{}.otio".format(otio_basename)),
            otio_str
        )

    return
