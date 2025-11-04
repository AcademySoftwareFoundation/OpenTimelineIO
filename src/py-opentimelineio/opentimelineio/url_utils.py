# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for conversion between urls and file paths"""

import os
import urllib
from urllib import request
import pathlib


def url_from_filepath(fpath):
    """Convert a filesystem path to an url in a portable way.

    ensures that `fpath` conforms to the following pattern:
        * if it is an absolute path, "file:///path/to/thing"
        * if it is a relative path, "path/to/thing"

    In other words, if you pass in:
        * "/var/tmp/thing.otio" -> "file:///var/tmp/thing.otio"
        * "subdir/thing.otio" -> "tmp/thing.otio"
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
    Take an url and return a filepath.

    URLs can either be encoded according to the `RFC 3986`_ standard or not.
    Additionally, Windows mapped drive letter and UNC paths need to be
    accounted for when processing URL(s); however, there are `ongoing
    discussions`_ about how to best handle this within Python developer
    community. This function is meant to cover these scenarios in the interim.

    .. _RFC 3986: https://tools.ietf.org/html/rfc3986#section-2.1
    .. _ongoing discussions: https://discuss.python.org/t/file-uris-in-python/15600
    """

    # Parse provided URL
    parsed_result = urllib.parse.urlparse(urlstr)

    # De-encode the parsed path
    decoded_parsed_path = urllib.parse.unquote(parsed_result.path)

    # Convert the parsed URL to a path
    filepath = pathlib.PurePath(
        request.url2pathname(decoded_parsed_path)
    )

    # If the network location is a window drive, reassemble the path
    if pathlib.PureWindowsPath(parsed_result.netloc).drive:
        filepath = pathlib.PurePath(parsed_result.netloc + decoded_parsed_path)

    # If the specified index is a windows drive, then append it to the other
    # parts
    elif pathlib.PureWindowsPath(filepath.parts[0]).drive:
        filepath = pathlib.PurePosixPath(filepath.drive, *filepath.parts[1:])

    # If the specified index is a windows drive, then offset the path
    elif (
        # relative paths may not have a parts[1]
        len(filepath.parts) > 1
        and pathlib.PureWindowsPath(filepath.parts[1]).drive
    ):
        # Remove leading "/" if/when `request.url2pathname` yields
        # "/S:/path/file.ext"
        filepath = pathlib.PurePosixPath(*filepath.parts[1:])

    # Should catch UNC paths,
    # as parsing "file:///some/path/to/file.ext" doesn't provide a netloc
    elif parsed_result.netloc and parsed_result.netloc != 'localhost':
        # Paths of type: "file://host/share/path/to/file.ext" provide "host" as
        # netloc
        filepath = pathlib.PurePath(
            '//',
            parsed_result.netloc + decoded_parsed_path
        )

        # Executing `as_posix` on Windows seems to generate a path with only 1
        # leading `/`, so we insert another `/` at the front of the string path
        # to match Linux and Windows UNC conventions and return it.
        conformed_filepath = filepath.as_posix()
        if not conformed_filepath.startswith('//'):
            conformed_filepath = '/' + conformed_filepath
        return conformed_filepath

    # Convert "\" to "/" if needed
    return filepath.as_posix()
