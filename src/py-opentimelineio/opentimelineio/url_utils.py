# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for conversion between URLs and file paths."""

import os
import urllib
from urllib import request
import pathlib

from ._otio import bundle


def url_from_filepath(fpath):
    """Convert a filesystem path to a URL in a portable way.

    ensures that `fpath` conforms to the following pattern:
        * if it is an absolute path, "file:///path/to/thing"
        * if it is a relative path, "path/to/thing"

    In other words, if you pass in:
        * "/var/tmp/thing.otio" -> "file:///var/tmp/thing.otio"
        * "tmp/thing.otio" -> "tmp/thing.otio"
    """

    try:
        # appears to handle absolute windows paths better, which are absolute
        # and start with a drive letter.
        return urllib.parse.unquote(pathlib.PurePath(fpath).as_uri())
    except ValueError:
        # scheme is "file" for absolute paths, else ""
        scheme = "file" if os.path.isabs(fpath) else ""

        # handles relative paths
        return urllib.parse.urlunparse(
            urllib.parse.ParseResult(
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
    Take a URL and return a filepath.

    Handles URLs encoded per `RFC 3986`_, Windows drive letters
    (``file://C:/...``), UNC paths (``file://host/share/...``), and the
    ``file://localhost/...`` variant.

    Raises :class:`ValueError` if the input uses a non-file scheme.

    .. _RFC 3986: https://tools.ietf.org/html/rfc3986#section-2.1
    """
    result = bundle.file_from_url(urlstr)
    if result is None:
        raise ValueError(
            "Cannot convert URL to filepath (non-file scheme): {!r}".format(urlstr)
        )
    return result
