#
# Copyright Contributors to the OpenTimelineIO project
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
ExternalReferences with target_urls to files with unique basenames that are
accessible through the file system and bundles those files and the otio file
into a single directory named with a suffix of .otiod.
"""

import os
import shutil

from . import (
    file_bundle_utils as utils,
    otio_json,
)

from .. import (
    exceptions,
    url_utils,
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
        new_fpath = url_utils.url_from_filepath(
            os.path.join(filepath, rel_path)
        )

        cl.media_reference.target_url = new_fpath

    return result


def write_to_file(
    input_otio,
    filepath,
    media_policy=utils.MediaReferencePolicy.ErrorIfNotFile,
    dryrun=False
):

    if os.path.exists(filepath):
        raise exceptions.OTIOError(
            "'{}' exists, will not overwrite.".format(filepath)
        )

    if not os.path.exists(os.path.dirname(filepath)):
        raise exceptions.OTIOError(
            "Directory '{}' does not exist, cannot create '{}'.".format(
                os.path.dirname(filepath),
                filepath
            )
        )

    if not os.path.isdir(os.path.dirname(filepath)):
        raise exceptions.OTIOError(
            "'{}' is not a directory, cannot create '{}'.".format(
                os.path.dirname(filepath),
                filepath
            )
        )

    # general algorithm for the file bundle adapters:
    # -------------------------------------------------------------------------
    # - build file manifest (list of paths to files on disk that will be put
    #   into the archive)
    # - build a mapping of path to file on disk to url to put into the media
    #   reference in the result
    # - relink the media references to point at the final location inside the
    #   archive
    # - build the resulting structure (zip file, directory)
    # -------------------------------------------------------------------------

    result_otio, path_to_mr_map = utils._prepped_otio_for_bundle_and_manifest(
        input_otio,
        media_policy,
        "OTIOD"
    )

    # dryrun reports the total size of files
    if dryrun:
        return utils._total_file_size_of(path_to_mr_map.keys())

    abspath_to_output_path_map = {}

    # relink all the media references to their target paths
    for abspath, references in path_to_mr_map.items():
        target = os.path.join(
            filepath,
            utils.BUNDLE_DIR_NAME,
            os.path.basename(abspath)
        )

        # conform to posix style paths inside the bundle, so that they are
        # portable between windows and *nix style environments
        final_path = str(pathlib.Path(target).as_posix())

        # cache the output path
        abspath_to_output_path_map[abspath] = final_path

        for mr in references:
            # author the relative path from the root of the bundle in url
            # form into the target_url
            mr.target_url = url_utils.url_from_filepath(
                os.path.relpath(final_path, filepath)
            )

    os.mkdir(filepath)

    # write the otioz file to the temp directory
    otio_json.write_to_file(
        result_otio,
        os.path.join(filepath, utils.BUNDLE_PLAYLIST_PATH)
    )

    # write the media files
    os.mkdir(os.path.join(filepath, utils.BUNDLE_DIR_NAME))
    for src, dst in abspath_to_output_path_map.items():
        shutil.copyfile(src, dst)

    return
