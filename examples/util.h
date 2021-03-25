#pragma once

#include <opentimelineio/errorStatus.h>

#include <vector>

#if defined(_WINDOWS)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif // WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#define NOMINMAX
#endif // NOMINMAX
#include <windows.h>
#endif // _WINDOWS

// Normalize a path (change '\' path delimeters to '/').
std::string normalize_path(std::string const&);

// Extract the directory from a file name.
std::string extract_dir(std::string const&);

// Convert to an absolute path.
std::string absolute_path(std::string const&);

// Create a temporary directory.
std::string create_temp_dir();

// Find files with simple pattern matching.
std::vector<std::string> glob(std::string const& pattern);

// Print an error to std::cerr.
void print_error(opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus const&);

#if defined(_WINDOWS)
class WCharBuffer
{
public:
    WCharBuffer(std::string const&);
    ~WCharBuffer();
    WCHAR* p = nullptr;
};
#endif // _WINDOWS
