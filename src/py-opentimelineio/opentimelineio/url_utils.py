# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for conversion between urls and file paths"""

import os

from urllib import (
    parse as urlparse,
    request
)
import pathlib


def url_from_filepath(fpath):
    """Convert a filesystem path to an url in a portable way using / path sep"""

    try:
        # appears to handle absolute windows paths better, which are absolute
        # and start with a drive letter.
        return urlparse.unquote(pathlib.Path(fpath).as_uri())
    except ValueError:
        # scheme is "file" for absolute paths, else ""
        scheme = "file" if os.path.isabs(fpath) else ""

        # handles relative paths
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


def filepath_from_url(urlstr):
    """ Take a url and return a filepath """

    parsed_result = urlparse.urlparse(urlstr)

    # Check if original urlstr is URL encoded
    if urlparse.unquote(urlstr) != urlstr:
        filepath = request.url2pathname(parsed_result.path)

    # Otherwise, combine the netloc and path
    else:
        filepath = parsed_result.netloc + parsed_result.path

    filepath = filepath.replace("\\", "/")

    # If on Windows, remove the first leading slash left by urlparse
    if os.name == 'nt' and filepath.startswith('/'):
        filepath = filepath[1:]

    return filepath
