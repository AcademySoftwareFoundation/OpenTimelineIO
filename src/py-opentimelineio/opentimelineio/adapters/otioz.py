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

Takes as input an OTIO file that has media references which are all
ExternalReferences with target_urls to files with unique basenames that are
accessible through the file system and bundles those files and the otio file
into a single zip file with the suffix .otioz.  Can error out if files aren't
locally referenced or provide missing references

Can also extract the content.otio file from an otioz bundle for processing.

Note that OTIOZ files _always_ use the unix style path separator ('/').  This
ensures that regardless of which platform a bundle was created on, it can be
read on unix and windows platforms.
"""

import os
import copy
import zipfile

from .. import (
    exceptions,
)

from . import (
    file_bundle_utils as utils,
    otio_json
)

try:
    import pathlib
except ImportError:
    # python2
    import pathlib2 as pathlib


try:
    # Python 2.7
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse


def read_from_file(filepath, extract_to_directory=None):
    if not zipfile.is_zipfile(filepath):
        raise exceptions.OTIOError("Not a zipfile: {}".format(filepath))

    if extract_to_directory:
        output_media_directory = os.path.join(
            extract_to_directory,
            utils.BUNDLE_DIR_NAME
        )

        if not os.path.exists(extract_to_directory):
            raise exceptions.OTIOError(
                "Directory '{}' does not exist, cannot unpack otioz "
                "there.".format(extract_to_directory)
            )

        if os.path.exists(output_media_directory):
            raise exceptions.OTIOError(
                "Error: '{}' already exists on disk, cannot overwrite while "
                " unpacking OTIOZ file '{}'.".format(
                    output_media_directory,
                    filepath
                )

            )

    with zipfile.ZipFile(filepath, 'r') as zi:
        result = otio_json.read_from_string(zi.read(utils.BUNDLE_PLAYLIST_PATH))

        if extract_to_directory:
            zi.extractall(extract_to_directory)

    return result


def write_to_file(
    input_otio,
    filepath,
    media_policy=utils.MediaReferencePolicy.ErrorIfNotFile,
    dryrun=False
):
    input_otio = copy.deepcopy(input_otio)

    manifest = utils._file_bundle_manifest(
        input_otio,
        filepath,
        media_policy,
        "OTIOZ"
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
        target = os.path.join(utils.BUNDLE_DIR_NAME, os.path.basename(fn))

        # conform to posix style paths inside the bundle, so that they are
        # portable between windows and *nix style environments
        fmapping[fn] = str(pathlib.Path(target).as_posix())

    # relink the media reference
    for cl in input_otio.each_clip():
        if media_policy == utils.MediaReferencePolicy.AllMissing:
            cl.media_reference = utils.reference_cloned_and_missing(
                cl.media_reference,
                "{} specified as the MediaReferencePolicy".format(media_policy)
            )
            continue

        try:
            source_url = urlparse.urlparse(cl.media_reference.target_url)
        except AttributeError:
            continue

        cl.media_reference.target_url = "file:{}".format(
            fmapping[source_url.path]
        )

    # write the otioz file to the temp directory
    otio_str = otio_json.write_to_string(input_otio)

    with zipfile.ZipFile(filepath, mode='w') as target:
        # write the version file (compressed)
        target.writestr(
            utils.BUNDLE_VERSION_FILE,
            utils.BUNDLE_VERSION,
            compress_type=zipfile.ZIP_DEFLATED
        )

        # write the OTIO (compressed)
        target.writestr(
            utils.BUNDLE_PLAYLIST_PATH,
            otio_str,
            # Python 3 use ZIP_LZMA
            compress_type=zipfile.ZIP_DEFLATED
        )

        # write the media (uncompressed)
        for src, dst in fmapping.items():
            target.write(src, dst, compress_type=zipfile.ZIP_STORED)

    return
