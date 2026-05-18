// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <iostream>
#include <memory>
#include <sstream>

#if defined(_WIN32)
#    if !defined(WIN32_LEAN_AND_MEAN)
#        define WIN32_LEAN_AND_MEAN
#    endif // WIN32_LEAN_AND_MEAN
#    include <combaseapi.h>
#    include <windows.h>
#    if defined(min)
#        undef min
#    endif // min
#else // _WIN32
#    include <unistd.h>
#endif // _WIN32

void
assertTrue(bool value)
{
    assert(value);
}

void
assertFalse(bool value)
{
    assert(!value);
}

#if defined(_WIN32)

TempDir::TempDir()
{
    // Create a unique name from a GUID.
    GUID guid;
    CoCreateGuid(&guid);
    const uint8_t* guidP = reinterpret_cast<const uint8_t*>(&guid);
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for (int i = 0; i < 16; ++i)
        ss << std::setw(2) << static_cast<int>(guidP[i]);

    auto path = std::filesystem::temp_directory_path() / ss.str();
    std::error_code ec;
    if (!std::filesystem::create_directory(path, ec))
        throw std::runtime_error("cannot create temp directory");
    _path = path;
}

#else // _WIN32

TempDir::TempDir()
{
    auto const path = (std::filesystem::temp_directory_path() / "XXXXXX").u8string();
    std::vector<char> buf(path.begin(), path.end());
    buf.push_back('\0');
    if (!mkdtemp(buf.data()))
        throw std::runtime_error("cannot create temp directory");
    _path = std::filesystem::u8path(buf.data());
}

#endif // _WIN32

TempDir::~TempDir()
{
    std::error_code ec;
    std::filesystem::remove_all(_path, ec);
}

void
Tests::add_test(std::string const& name, std::function<void(void)> const& test)
{
    _tests.push_back(std::make_pair(name, test));
}

void
Tests::run(int argc, char** argv)
{
    std::vector<std::string> filter;
    for (int arg = 1; arg < argc; ++arg)
    {
        filter.push_back(argv[arg]);
    }

    for (auto const& test: _tests)
    {
        bool run_test = true;
        if (!filter.empty())
        {
            const auto filter_it =
                std::find(filter.begin(), filter.end(), test.first);
            run_test = filter_it != filter.end();
        }

        std::cout << (run_test ? "Running" : "Skipping") << " test "
                  << test.first << std::endl;
        if (run_test)
        {
            test.second();
        }
    }
}
