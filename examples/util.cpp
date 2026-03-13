// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "util.h"

#include "opentimelineio/fileUtils.h"
#include <opentimelineio/timeline.h>

#include <Python.h>

#include <codecvt>
#include <iostream>
#include <locale>

#if defined(_WINDOWS)
#if !defined(WIN32_LEAN_AND_MEAN)
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#include <windows.h>
#if defined(min)
#undef min
#endif // min
#else // _WINDOWS
#include <sys/types.h>
#include <dirent.h>
#include <fnmatch.h>
#include <stdlib.h>
#include <unistd.h>
#endif // _WINDOWS

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION_NS;

namespace examples {

#if defined(_WINDOWS)

std::string absolute(std::string const& in)
{
    wchar_t buf[MAX_PATH];
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> utf16;
    if (!::_wfullpath(buf, utf16.from_bytes(in).c_str(), MAX_PATH))
    {
        buf[0] = 0;
    }
    return otio::to_unix_separators(utf16.to_bytes(buf));
}

std::vector<std::string> glob(std::string const& path, std::string const& pattern)
{
    std::vector<std::string> out;

    // Prepare the path.
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> utf16;
    std::wstring wpath = utf16.from_bytes(path + '/' + pattern);
    WCHAR wbuf[MAX_PATH];
    size_t size = std::min(wpath.size(), static_cast<size_t>(MAX_PATH - 1));
    memcpy(wbuf, wpath.c_str(), size * sizeof(WCHAR));
    wbuf[size++] = 0;

    // List the directory contents.
    std::string const absolutePath = absolute(path);
    WIN32_FIND_DATAW ffd;
    HANDLE hFind = FindFirstFileW(wbuf, &ffd);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        do
        {
            out.push_back(absolutePath + '/' + utf16.to_bytes(ffd.cFileName));
        } while (FindNextFileW(hFind, &ffd) != 0);
        FindClose(hFind);
    }

    return out;
}

#else // _WINDOWS

std::string absolute(std::string const& in)
{
    char buf[PATH_MAX];
    if (NULL == realpath(in.c_str(), buf))
    {
        buf[0] = 0;
    }
    return buf;
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

}

