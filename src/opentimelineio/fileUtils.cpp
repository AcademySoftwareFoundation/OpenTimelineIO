// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/fileUtils.h"

#include <cstdio>
#include <filesystem>
#include <iostream>

#if !defined(_WINDOWS)
#include <stdlib.h>
#include <unistd.h>
#endif // _WINDOWS

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
#if defined(_WINDOWS)
    // \todo Replace std::tmpnam() since it is potentially unsafe.
    std::string const out(std::tmpnam(nullptr));
    std::filesystem::create_directory(out);
#else // _WINDOWS
    std::string dir = std::filesystem::temp_directory_path() / "XXXXXX";
    if (mkdtemp(dir.data()))
    {
        out = dir;
    }
#endif // _WINDOWS
    return out;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
