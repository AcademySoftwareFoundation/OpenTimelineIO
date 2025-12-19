// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/urlUtils.h"

#include "opentimelineio/fileUtils.h"

#include <uriparser/Uri.h>

#include <filesystem>
#include <iostream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

std::string
scheme_from_url(std::string const& url)
{
    std::string out;
    UriUriA uri;
    const char* uri_error_pos = nullptr;
    if (uriParseSingleUriA(&uri, url.c_str(), &uri_error_pos) == URI_SUCCESS)
    {
        if (uri.scheme.first)
        {
            out = std::string(uri.scheme.first, uri.scheme.afterLast - uri.scheme.first);
        }
        uriFreeUriMembersA(&uri);
    }
    return out;
}

std::string
url_from_filepath(std::string const& filepath)
{
    std::cout << "url_from_filepath()" << std::endl;
    std::cout << "  filepath: " << filepath << std::endl;
    std::string out;
    //std::string tmp(8 + 3 * filepath.size() + 1, 0);
    //if (uriWindowsFilenameToUriStringA(filepath.c_str(), tmp.data()) == URI_SUCCESS)
    std::vector<char> tmp(7 + 3 * filepath.size() + 1, 0);
    if (uriUnixFilenameToUriStringA(filepath.c_str(), tmp.data()) == URI_SUCCESS &&
        !tmp.empty())
    {
        out = std::string(tmp.data());
    }
    std::cout << "  out: " << out.c_str() << std::endl;
    return out;
}

std::string
filepath_from_url(std::string const& url)
{
    std::cout << "filepath_from_url()" << std::endl;
    std::cout << "  url: " << url << std::endl;
    std::string out;
    //std::string tmp(url.size() + 1, 0);
    //if (uriUriStringToWindowsFilenameA(url.c_str(), tmp.data()) == URI_SUCCESS)
    std::vector<char> tmp(url.size() + 1, 0);
    if (uriUriStringToUnixFilenameA(url.c_str(), tmp.data()) == URI_SUCCESS &&
        !tmp.empty())
    {
        out = std::string(tmp.data());
    }
    std::cout << "  out: " << out.c_str() << std::endl;
    return out;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
