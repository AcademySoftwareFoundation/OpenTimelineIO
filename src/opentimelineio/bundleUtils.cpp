// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundleUtils.h"

#include <algorithm>
#include <filesystem>
#include <iomanip>
#include <regex>
#include <sstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace bundle {

namespace {

std::string
url_encode(std::string const& url)
{
    // Don't encode these characters.
    const std::vector<char> chars = { '-', '.', '_', '~', ':', '/', '?',  '#',
                                      '[', ']', '@', '!', '$', '&', '\'', '(',
                                      ')', '*', '+', ',', ';', '=', '\\' };

    // Copy characters to the result, encoding if necessary.
    std::stringstream ss;
    ss.fill('0');
    ss << std::hex;
    for (auto i = url.begin(), end = url.end(); i != end; ++i)
    {
        const auto j = std::find(chars.begin(), chars.end(), *i);
        if (std::isalnum(*i) || j != chars.end())
        {
            ss << *i;
        }
        else
        {
            ss << '%' << std::setw(2) << int(*i);
        }
    }
    return ss.str();
}

std::string
url_decode(std::string const& url)
{
    std::string result;

    // Find all percent encodings.
    size_t           url_pos = 0;
    const std::regex rx("(%[0-9A-Fa-f][0-9A-Fa-f])");
    for (auto i = std::sregex_iterator(url.begin(), url.end(), rx);
         i != std::sregex_iterator();
         ++i)
    {

        // Copy parts without any encodings.
        if (url_pos != static_cast<size_t>(i->position()))
        {
            result.append(url.substr(url_pos, i->position() - url_pos));
            url_pos = i->position() + i->str().size();
        }

        // Convert the encoding and append it.
        std::stringstream ss;
        ss << std::hex << i->str().substr(1);
        unsigned int j = 0;
        ss >> j;
        result.push_back(char(j));
    }

    // Copy the remainder without any encodings.
    if (!url.empty() && url_pos != url.size() - 1)
    {
        result.append(url.substr(url_pos, url.size() - url_pos));
    }

    return result;
}

} // namespace


std::string
to_unix_separators(const std::string& path)
{
    std::string result = path;
    std::replace(result.begin(), result.end(), '\\', '/');
    return result;
}

std::string
url_from_filepath(std::string const& filepath)
{
    const std::string encoded = url_encode(filepath);
    const std::string url     = std::filesystem::u8path(filepath).is_relative()
                                    ? encoded
                                    : ("file://" + encoded);
    return url;
}

std::string
filepath_from_url(std::string const& url)
{
    // Skip over the URL scheme.
    bool       has_scheme = false;
    size_t     pos        = 0;
    std::regex rx("^([A-Za-z0-9+-\\.]+://)");
    auto       rxi = std::sregex_iterator(url.begin(), url.end(), rx);
    if (rxi != std::sregex_iterator())
    {
        has_scheme = true;
        pos += rxi->str().size();
    }

    // Remove the URL query and fragment.
    size_t size = std::string::npos;
    size_t i    = url.find('?', pos);
    size_t j    = url.find('#', pos);
    if (i != std::string::npos || j != std::string::npos)
    {
        size = std::min(i, j) + 1;
    }
    const std::string path = url.substr(pos, size);

    // Decode the path.
    std::string decoded = url_decode(path);

    // Use UNIX separators.
    decoded = to_unix_separators(decoded);

    // Check for Windows drive letters.
    bool has_windows_drive = false;
    rx                     = std::regex("^([A-Za-z]:)");
    std::smatch matches;
    if (std::regex_search(decoded, matches, rx))
    {
        has_windows_drive = true;
    }
    else
    {
        rx = std::regex("^(.*/)([A-Za-z]:)");
        if (std::regex_search(decoded, matches, rx))
        {
            has_windows_drive = true;
            decoded = decoded.substr(matches.position(1) + matches.length(1));
        }
    }

    // Add the "//" for UNC paths.
    bool has_unc = false;
    size         = decoded.size();
    if (has_scheme && !has_windows_drive && pos < size - 1 && decoded[0] != '/')
    {
        has_unc = true;
        decoded.insert(0, "//");
    }

    // Remove the current directory.
    rx = std::regex("^(./)");
    if (!has_windows_drive && !has_unc
        && std::regex_search(decoded, matches, rx))
    {
        decoded = decoded.substr(matches.position() + matches.length());
    }

    return decoded;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
