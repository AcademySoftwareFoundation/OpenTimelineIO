#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

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
    """convert a filesystem path to an url in a portable way using / path sep"""

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
