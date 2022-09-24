# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for conversion between urls and file paths"""

import os

try:
    # Python 2.7
    import urlparse
    import urllib
except ImportError:
    # Python 3
    import urllib.parse as urlparse
    from urllib import request as urllib

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


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
    return urllib.url2pathname(parsed_result.path)
