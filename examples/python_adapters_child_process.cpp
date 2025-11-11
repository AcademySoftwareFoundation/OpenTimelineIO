// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

// Example OTIO C++ code for reading and writing files supported by the OTIO
// Python adapters.
//
// This example uses the "otioconvert" utility in a child process to convert
// between input/output files and JSON that can be used from C++ code.
//
// To run this example make sure that the "otioconvert" utility is in your
// search path and the environment variable PYTHONPATH is set correctly.

#include "util.h"

#include <opentimelineio/timeline.h>

#include <iostream>
#include <sstream>

#if defined(_WINDOWS)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#include <cctype>
#include <codecvt>
#include <locale>
#include <windows.h>
#include <combaseapi.h>
#else // _WINDOWS
#include <stdio.h>
#endif // _WINDOWS

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION_NS;

class PythonAdapters
{
public:
    static otio::SerializableObject::Retainer<otio::Timeline> read_from_file(
        std::string const&,
        otio::ErrorStatus*);

    static bool write_to_file(
        otio::SerializableObject::Retainer<otio::Timeline> const&,
        std::string const&,
        otio::ErrorStatus*);

private:
    static bool _run_process(std::string const& cmd_line, otio::ErrorStatus*);
};

otio::SerializableObject::Retainer<otio::Timeline> PythonAdapters::read_from_file(
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    // Convert the input file to a temporary JSON file.
    const std::string temp_file_name = examples::create_temp_dir() + "/temp.otio";
    std::stringstream ss;
    ss << "otioconvert" << " -i " << examples::normalize_path(file_name) << " -o " << temp_file_name;
    _run_process(ss.str(), error_status);

    // Read the temporary JSON file.
    return dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(temp_file_name, error_status));
}

bool PythonAdapters::write_to_file(
    otio::SerializableObject::Retainer<otio::Timeline> const& timeline,
    std::string const& file_name,
    otio::ErrorStatus* error_status)
{
    // Write the temporary JSON file.
    const std::string temp_file_name = examples::create_temp_dir() + "/temp.otio";
    if (!timeline.value->to_json_file(temp_file_name, error_status))
    {
        return false;
    }

    // Convert the temporary JSON file to the output file.
    std::stringstream ss;
    ss << "otioconvert" << " -i " << temp_file_name << " -o " << examples::normalize_path(file_name);
    _run_process(ss.str(), error_status);

    return true;
}

#if defined(_WINDOWS)

class WCharBuffer
{
public:
    WCharBuffer(const WCHAR* data, size_t size)
    {
        p = new WCHAR[(size + 1) * sizeof(WCHAR)];
        memcpy(p, data, size * sizeof(WCHAR));
        p[size] = 0;
    }

    ~WCharBuffer()
    {
        delete[] p;
    }

    WCHAR* p = nullptr;
};

bool PythonAdapters::_run_process(const std::string& cmd_line, otio::ErrorStatus* error_status)
{
    // Convert the command-line to UTF16.
    std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> utf16;
    std::wstring w_cmd_line = utf16.from_bytes("/c " + cmd_line);
    WCharBuffer w_cmd_line_buf(w_cmd_line.c_str(), w_cmd_line.size());

    // Create the process and wait for it to complete.
    STARTUPINFOW si;
    ZeroMemory(&si, sizeof(si));
    PROCESS_INFORMATION pi;
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    if (0 == CreateProcessW(
        // TODO: MSDN documentation says to use "cmd.exe" for the "lpApplicationName"
        // argument, but that gives the error: "The system cannot find the file specified."
        // https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw
        //L"cmd.exe",
        L"C:\\windows\\system32\\cmd.exe",
        w_cmd_line_buf.p,
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi))
    {
        const DWORD error = GetLastError();
        TCHAR error_buf[4096];
        FormatMessage(
            FORMAT_MESSAGE_FROM_SYSTEM |
            FORMAT_MESSAGE_IGNORE_INSERTS,
            NULL,
            error,
            MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
            error_buf,
            4096,
            NULL);
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_OPEN_FAILED;
        error_status->details = "cannot create process: " + std::string(error_buf, lstrlen(error_buf));
        return false;
    }
    WaitForSingleObject(pi.hProcess, INFINITE);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return true;
}

#else // _WINDOWS

bool PythonAdapters::_run_process(const std::string& cmd_line, otio::ErrorStatus* error_status)
{
    FILE* f = popen(cmd_line.c_str(), "r");
    if (!f)
    {
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_OPEN_FAILED;
        error_status->details = "cannot create process";
        return false;
    }
    if (-1 == pclose(f))
    {
        error_status->outcome = otio::ErrorStatus::Outcome::FILE_OPEN_FAILED;
        error_status->details = "cannot execute process";
        return false;
    }
    return true;
}

#endif // _WINDOWS

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "Usage: python_adapters_child_process (inputpath) (outputpath)" << std::endl;
        return 1;
    }

    otio::ErrorStatus error_status;
    auto timeline = PythonAdapters::read_from_file(argv[1], &error_status);
    if (!timeline)
    {
        examples::print_error(error_status);
        return 1;
    }

    std::cout << "Video tracks: " << timeline.value->video_tracks().size() << std::endl;
    std::cout << "Audio tracks: " << timeline.value->audio_tracks().size() << std::endl;

    if (!PythonAdapters::write_to_file(timeline, argv[2], &error_status))
    {
        examples::print_error(error_status);
        return 1;
    }

    return 0;
}
