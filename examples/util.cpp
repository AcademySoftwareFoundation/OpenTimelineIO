#include "util.h"

#include <opentimelineio/timeline.h>

#include <Python.h>

#include <iostream>

#if defined(_WINDOWS)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <combaseapi.h>
#else // _WINDOWS
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <fnmatch.h>
#include <stdlib.h>
#include <unistd.h>
#endif // _WINDOWS

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

#if defined(_WINDOWS)

std::string normalize_path(std::string const& in)
{
    std::string out;
    for (auto i : in)
    {
        out.push_back('\\' == i ? '/' : i);
    }
    return out;
}

std::string absolute(std::string const& path)
{
    return path;
}

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

std::vector<std::string> glob(std::string const& in)
{
    std::vector<std::string> out;
    return out;
}

#else // _WINDOWS

std::string normalize_path(std::string const& in)
{
    return in;
}

std::string absolute(std::string const& path)
{
    char buf[PATH_MAX];
    realpath(path.c_str(), buf);
    return buf;
}

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

std::vector<std::string> glob(std::string const& path, std::string const& pattern)
{
    std::vector<std::string> out;
    std::string const absolutePath = absolute(path);
    DIR* dir = opendir(path.c_str());
    if (dir)
    {
        struct dirent* e = nullptr;
        while ((e = readdir(dir)) != nullptr)
        {
            if (0 == fnmatch(pattern.c_str(), e->d_name, 0))
            {
                out.push_back(absolutePath + '/' + e->d_name);
            }
        }
        closedir(dir);
    }
    return out;
}

#endif // _WINDOWS

void print_error(otio::ErrorStatus const& error_status)
{
    std::cout << "ERROR: " <<
        otio::ErrorStatus::outcome_to_string(error_status.outcome) << ": " <<
        error_status.details << std::endl;
}

