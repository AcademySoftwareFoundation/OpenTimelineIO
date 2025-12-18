// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/fileUtils.h"

#include <cstdio>
#include <filesystem>
#include <iostream>

#if !defined(_WIN32)
#include <stdlib.h>
#include <unistd.h>
#endif // _WIN32

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
    std::string out;
#if defined(_WIN32)
    // \todo Replace std::tmpnam() since it is potentially unsafe.
    out = std::tmpnam(nullptr);
    std::filesystem::create_directory(out);
#else // _WIN32
    std::string dir = (std::filesystem::temp_directory_path() / "XXXXXX").u8string();
    if (mkdtemp(dir.data()))
    {
        out = dir;
    }
#endif // _WIN32
    return out;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
