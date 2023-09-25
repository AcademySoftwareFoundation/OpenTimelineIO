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

    parsed_result = urlparse.urlparse(urlstr)

    # Check if original urlstr is URL encoded
    if urlparse.unquote(urlstr) != urlstr:
        filepath = request.url2pathname(parsed_result.path)

    # Otherwise, combine the netloc and path
    else:
        filepath = parsed_result.netloc + parsed_result.path

    filepath = filepath.replace("\\", "/")

    # If on Windows and using a drive letter,
    # remove the first leading slash left by urlparse
    if re.match(r"/[a-zA-Z]:/.*", filepath):
        filepath = filepath[1:]

    return filepath
