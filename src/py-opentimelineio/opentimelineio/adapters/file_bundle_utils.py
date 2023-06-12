# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Common utilities used by the file bundle adapters (otiod and otioz)."""

import os
import copy


from .. import (
    exceptions,
    schema,
    url_utils,
)

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


def _guarantee_unique_basenames(path_list, adapter_name):
    # walking across all unique file references, guarantee that all the
    # basenames are unique
    basename_to_source_fn = {}
    for fn in path_list:
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


def _prepped_otio_for_bundle_and_manifest(
    input_otio,    # otio to process
    media_policy,  # what to do with media references
    adapter_name,  # just for error messages
):
    """ Create a new OTIO based on input_otio that has had media references
    replaced according to the media_policy.  Return that new OTIO and a
    list of all the absolute file paths (not URLs) to be used in the bundle.
    Media references in the OTIO will be relinked by the adapters to point to
    their output locations.

    The otio[dz] adapters use this function to do further relinking and build
    their bundles.

    This is considered an internal API.
    """

    # make sure the incoming OTIO isn't edited
    result_otio = copy.deepcopy(input_otio)

    paths = set()
    invalid_files = set()

    # result_otio is manipulated in place
    for cl in result_otio.find_clips():
        if media_policy == MediaReferencePolicy.AllMissing:
            cl.media_reference = reference_cloned_and_missing(
                cl.media_reference,
                f"{media_policy} specified as the MediaReferencePolicy"
            )
            continue

        for mr in cl.media_references().values():
            if isinstance(mr, schema.ImageSequenceReference):
                url = cl.media_reference.target_url_base
            else:
                try:
                    url = cl.media_reference.target_url
                except AttributeError:
                    # not an ImageSequenceReference or object with target_url,
                    # ignoring it.
                    continue

            parsed_url = urlparse.urlparse(url)

            # ensure that the urlscheme is either file or ""
            # file means "absolute path"
            # none is interpreted as a relative path, relative to cwd
            if parsed_url.scheme not in ("file", ""):
                if media_policy is MediaReferencePolicy.ErrorIfNotFile:
                    raise NotAFileOnDisk(
                        "The {} adapter only works with file URLs."
                        " Got a URL of:  '{}'".format(adapter_name, url)
                    )
                if media_policy is MediaReferencePolicy.MissingIfNotFile:
                    cl.media_reference = reference_cloned_and_missing(
                        cl.media_reference,
                        "not a file URL"
                    )
                    continue

            # get absolute paths to the target files
            target_files = []
            if isinstance(mr, schema.ImageSequenceReference):
                for number in range(mr.number_of_images_in_sequence()):
                    target_files.append(os.path.abspath(
                        url_utils.filepath_from_url(
                            mr.target_url_for_image_number(number))))
            else:
                target_files.append(os.path.abspath(
                    url_utils.filepath_from_url(url)))

            # if the file hasn't already been checked
            for target_file in target_files:
                if (
                    target_file not in paths
                    and target_file not in invalid_files
                    and (
                        not os.path.exists(target_file)
                        or not os.path.isfile(target_file)
                    )
                ):
                    invalid_files.add(target_file)

            invalid = False
            for target_file in target_files:
                if target_file in invalid_files:
                    if media_policy is MediaReferencePolicy.ErrorIfNotFile:
                        raise NotAFileOnDisk(target_file)
                    invalid = True
                    break
            if invalid:
                if media_policy is MediaReferencePolicy.MissingIfNotFile:
                    cl.media_reference = reference_cloned_and_missing(
                        cl.media_reference,
                        "not a file URL or does not exist"
                    )

                    # do not need to relink it in the future or add this target to
                    # the manifest, because the path is either not a file or does
                    # not exist.
                    continue

            # add the media reference to the list of references that point at this
            # file, they will need to be relinked
            for target_file in target_files:
                paths.add(target_file)

    _guarantee_unique_basenames(paths, adapter_name)

    return result_otio, list(paths)


def _total_file_size_of(filepaths):
    fsize = 0
    for fn in filepaths:
        fsize += os.path.getsize(fn)
    return fsize
