# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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
    schema,
    url_utils,
)

import pathlib
import urllib.parse as urlparse


def read_from_file(filepath, absolute_media_reference_paths=False):
    result = otio_json.read_from_file(
        os.path.join(filepath, utils.BUNDLE_PLAYLIST_PATH)
    )

    if not absolute_media_reference_paths:
        return result

    for cl in result.find_clips():
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
            f"'{filepath}' exists, will not overwrite."
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
    # - build a mapping of input paths to output paths
    # - relink the media references to point at the final location inside the
    #   archive
    # - build the resulting structure (zip file, directory)
    # -------------------------------------------------------------------------

    result_otio, paths = utils._prepped_otio_for_bundle_and_manifest(
        input_otio,
        media_policy,
        "OTIOD"
    )

    # dryrun reports the total size of files
    if dryrun:
        return utils._total_file_size_of(paths)

    # get the output paths
    abspath_to_output_path_map = {}
    for abspath in paths:
        target = os.path.join(
            filepath,
            utils.BUNDLE_DIR_NAME,
            os.path.basename(abspath)
        )
        abspath_to_output_path_map[abspath] = target

    # relink all the media references to their target paths
    for cl in result_otio.find_clips():
        for mr in cl.media_references().values():
            if isinstance(mr, schema.ImageSequenceReference):
                url = cl.media_reference.target_url_base
            else:
                try:
                    url = cl.media_reference.target_url
                except AttributeError:
                    continue

            target = os.path.join(
                utils.BUNDLE_DIR_NAME,
                os.path.basename(url_utils.filepath_from_url(url)))

            # conform to posix style paths inside the bundle, so that they are
            # portable between windows and *nix style environments
            final_path = str(pathlib.Path(target).as_posix())

            # author the final_path in url form into the media reference
            url = url_utils.url_from_filepath(final_path)
            if isinstance(mr, schema.ImageSequenceReference):
                mr.target_url_base = url if url.endswith('/') else url + '/'
            else:
                mr.target_url = url

    os.mkdir(filepath)

    # write the otio file
    otio_json.write_to_file(
        result_otio,
        os.path.join(filepath, utils.BUNDLE_PLAYLIST_PATH)
    )

    # write the media files
    os.mkdir(os.path.join(filepath, utils.BUNDLE_DIR_NAME))
    for src, dst in abspath_to_output_path_map.items():
        shutil.copyfile(src, dst)

    return
