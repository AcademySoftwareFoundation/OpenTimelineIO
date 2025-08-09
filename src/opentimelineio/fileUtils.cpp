// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/fileUtils.h"

#include <cstdio>
#include <filesystem>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

std::string
to_unix_separators(std::string const& path)
{
    std::string result = path;
    std::replace(result.begin(), result.end(), '\\', '/');
    return result;
}

std::string create_temp_dir()
{
    // \todo Replace std::tmpnam(), since it is potentially unsafe. A possible
    // replacement might be mkdtemp(), but that does not seem to be available
    // on Cygwin.
    std::string const out(std::tmpnam(nullptr));
    std::filesystem::create_directory(out);
    return out;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
