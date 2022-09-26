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

import os
import zipfile

from .. import (
    exceptions,
    url_utils,
)

from . import (
    file_bundle_utils as utils,
    otio_json
)

import pathlib


def read_from_file(filepath, extract_to_directory=None):
    if not zipfile.is_zipfile(filepath):
        raise exceptions.OTIOError(f"Not a zipfile: {filepath}")

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

    if os.path.exists(filepath):
        raise exceptions.OTIOError(
            f"'{filepath}' exists, will not overwrite."
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
        "OTIOZ"
    )

    # dryrun reports the total size of files
    if dryrun:
        return utils._total_file_size_of(path_to_mr_map.keys())

    abspath_to_output_path_map = {}

    # relink all the media references to their target paths
    for abspath, references in path_to_mr_map.items():
        target = os.path.join(utils.BUNDLE_DIR_NAME, os.path.basename(abspath))

        # conform to posix style paths inside the bundle, so that they are
        # portable between windows and *nix style environments
        final_path = str(pathlib.Path(target).as_posix())

        # cache the output path
        abspath_to_output_path_map[abspath] = final_path

        for mr in references:
            # author the final_path in url form into the target_url
            mr.target_url = url_utils.url_from_filepath(final_path)

    # write the otioz file to the temp directory
    otio_str = otio_json.write_to_string(result_otio)

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
        for src, dst in abspath_to_output_path_map.items():
            target.write(src, dst, compress_type=zipfile.ZIP_STORED)

    return
