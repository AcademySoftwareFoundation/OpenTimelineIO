# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for conversion between urls and file paths"""

import os
from urllib import (
    parse as urlparse,
    request
)
from pathlib import (
    PurePath,
    PureWindowsPath,
    PurePosixPath
)


def url_from_filepath(fpath):
    """Convert a filesystem path to an url in a portable way using / path sep"""

    try:
        # appears to handle absolute windows paths better, which are absolute
        # and start with a drive letter.
        return urlparse.unquote(PurePath(fpath).as_uri())
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
    Additionally, Windows mapped drive letter and UNC paths need to be accounted for
    when processing URL(s); however, there are `ongoing discussions`_ about how to best
    handle this within Python developer community. This function is meant to cover
    these scenarios in the interim.

    .. _RFC 3986: https://tools.ietf.org/html/rfc3986#section-2.1
    .. _ongoing discussions: https://discuss.python.org/t/file-uris-in-python/15600
    """

    # De-encode the URL
    decoded_url_str = urlparse.unquote(urlstr)

    # Parse provided URL
    parsed_result = urlparse.urlparse(decoded_url_str)

    # Convert the parsed URL to a path
    filepath = PurePath(request.url2pathname(parsed_result.path))

    # If the network location is a window drive, reassemble the path
    if PureWindowsPath(parsed_result.netloc).drive:
        filepath = PurePath(parsed_result.netloc + parsed_result.path)

    # Check if the specified index has a specified `drive`, if so then do nothing
    elif filepath.drive:
        filepath = filepath

    # Check if the specified index is a windows drive, then offset the path
    elif PureWindowsPath(filepath.parts[1]).drive:
        # Remove leading "/" if/when `request.url2pathname` yields "/S:/path/file.ext"
        filepath = PurePosixPath(*filepath.parts[1:])

    # Last resort, strip the "file:" prefix
    else:
        filepath = Path(decoded_url_str.strip('file:'))

    # Convert "\" to "/" if needed
    return filepath.as_posix()
