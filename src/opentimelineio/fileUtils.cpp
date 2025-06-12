// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/fileUtils.h"

#include <cstring>
#include <vector>

#if defined(_WINDOWS)
#if !defined(WIN32_LEAN_AND_MEAN)
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <combaseapi.h>
#if defined(min)
#undef min
#endif // min
#else // _WINDOWS
#include <sys/stat.h>
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

#if defined(_WINDOWS)

std::string create_temp_dir()
{
    std::string out;

    // Get the temporary directory.
    char path[MAX_PATH];
    DWORD r = GetTempPath(MAX_PATH, path);
    if (r)
    {
        out = std::string(path);

        // Replace path separators.
        for (size_t i = 0; i < out.size(); ++i)
        {
            if ('\\' == out[i])
            {
                out[i] = '/';
            }
        }

        // Create a unique name from a GUID.
        GUID guid;
        CoCreateGuid(&guid);
        const uint8_t* guidP = reinterpret_cast<const uint8_t*>(&guid);
        for (int i = 0; i < 16; ++i)
        {
            char buf[3] = "";
            sprintf_s(buf, 3, "%02x", guidP[i]);
            out += buf;
        }

        // Create a unique directory.
        CreateDirectory(out.c_str(), NULL);
    }

    return out;
}

#else // _WINDOWS

std::string create_temp_dir()
{
    // Find the temporary directory.
    std::string path;
    char* env = nullptr;
    if ((env = getenv("TEMP"))) path = env;
    else if ((env = getenv("TMP"))) path = env;
    else if ((env = getenv("TMPDIR"))) path = env;
    else
    {
        for (const auto& i : { "/tmp", "/var/tmp", "/usr/tmp" })
        {
            struct stat buffer;   
            if (0 == stat(i, &buffer))
            {
                path = i;
                break;
            }
        }
    }

    // Create a unique directory.
    path = path + "/XXXXXX";
    const size_t size = path.size();
    std::vector<char> buf(size + 1);
    memcpy(buf.data(), path.c_str(), size);
    buf[size] = 0;
    return mkdtemp(buf.data());
}

#endif // _WINDOWS

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
