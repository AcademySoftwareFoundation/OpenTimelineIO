# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for conversion between urls and file paths"""

import os
import re

from urllib import (
    parse as urlparse,
    request
)
import pathlib
from pathlib import Path, PureWindowsPath


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
    """
    Take an url and return a filepath.

    URLs can either be encoded according to the `RFC 3986`_ standard or not.
    Additionally, Windows mapped paths need to be accounted for when processing a
    URL; however, there are `ongoing discussions`_ about how to best handle this within
    Python. This function is meant to cover all of these scenarios in the interim.

    .. _RFC 3986: https://tools.ietf.org/html/rfc3986#section-2.1
    .. _ongoing discussions: https://discuss.python.org/t/file-uris-in-python/15600
    """

    # Parse provided URL
    parsed_result = urlparse.urlparse(urlstr)

    # Convert the parsed URL to a path
    filepath = Path(request.url2pathname(parsed_result.path))

    # If the network location is a window drive, reassemble the path
    if PureWindowsPath(parsed_result.netloc).drive:
        filepath = Path(parsed_result.netloc + parsed_result.path)

    # Otherwise check if the specified index is a windows drive, then offset the path
    elif PureWindowsPath(filepath.parts[1]).drive:
        # Remove leading "/" if/when `request.url2pathname` yields "/S:/path/file.ext"
        filepath = filepath.relative_to(filepath.root)

    # Convert "\" to "/" if needed
    return filepath.as_posix()
