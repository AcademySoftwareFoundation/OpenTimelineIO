#include "util.h"

#include <opentimelineio/timeline.h>

#include <Python.h>

#include <codecvt>
#include <iostream>
#include <locale>

#if defined(_WINDOWS)
#include <combaseapi.h>
#else // _WINDOWS
#include <sys/stat.h>
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

std::string extract_dir(std::string const& in)
{
    size_t i = in.find_last_of('\\');
    if (std::string::npos == i)
    {
        i = in.find_last_of('/');
    }
    return in.substr(0, i);
}

std::string absolute_path(std::string const& in)
{
    wchar_t buf[MAX_PATH];
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> utf16;
    if (!::_wfullpath(buf, utf16.from_bytes(in).c_str(), MAX_PATH))
    {
        buf[0] = 0;
    }
    return normalize_path(utf16.to_bytes(buf));
}

std::string create_temp_dir()
{
    std::string out;

    // Get the temporary directory.
    char path[MAX_PATH];
    DWORD r = GetTempPath(MAX_PATH, path);
    if (r)
    {
        // Replace path separators.
        out = normalize_path(path);

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

std::vector<std::string> glob(std::string const& pattern)
{
    std::vector<std::string> out;
    WCharBuffer w_buf(pattern);
    WIN32_FIND_DATAW ffd;
    HANDLE hFind = FindFirstFileW(w_buf.p, &ffd);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        const std::string path = extract_dir(normalize_path(pattern));
        std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> utf16;
        do
        {
            out.push_back(path + '/' + utf16.to_bytes(ffd.cFileName));
        } while (FindNextFileW(hFind, &ffd) != 0);
        FindClose(hFind);
    }
    return out;
}

WCharBuffer::WCharBuffer(std::string const& in)
{
    const std::wstring win = std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t>().from_bytes(in);
    const size_t size = win.size();
    p = new WCHAR[(size + 1) * sizeof(WCHAR)];
    memcpy(p, win.c_str(), size * sizeof(WCHAR));
    p[size] = 0;
}

WCharBuffer::~WCharBuffer()
{
    delete[] p;
}

#else // _WINDOWS

std::string normalize_path(std::string const& in)
{
    return in;
}

std::string extract_dir(std::string const& in)
{
    return in.substr(0, in.find_last_of('/'));
}

std::string absolute_path(std::string const& in)
{
    return {};
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

std::vector<std::string> glob(std::string const& path)
{
    return {};
}

#endif // _WINDOWS

void print_error(otio::ErrorStatus const& error_status)
{
    std::cout << "ERROR: " <<
        otio::ErrorStatus::outcome_to_string(error_status.outcome) << ": " <<
        error_status.details << std::endl;
}
