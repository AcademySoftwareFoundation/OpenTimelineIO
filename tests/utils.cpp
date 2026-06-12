// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <charconv>
#include <iostream>
#include <random>

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

TempDir::TempDir()
{
    // Generate a unique temporary directory name without platform-specific
    // routines. A 64-bit random value rendered as hex is plenty of entropy
    // to avoid collisions between concurrent tests; the generator is
    // thread_local so concurrent tests draw from independent streams.
    static thread_local std::mt19937_64 generator(std::random_device{}());

    auto const temp_root = std::filesystem::temp_directory_path();

    // Retry on the (extremely unlikely) chance the name already exists.
    for (int attempt = 0; attempt < 16; ++attempt)
    {
        uint64_t const rand_num = generator();

        // 16 hex digits max for a 64-bit value; size the buffer generously.
        char buf[32];
        auto const result =
            std::to_chars(buf, buf + sizeof(buf), rand_num, 16);
        std::string const name =
            "otio_tmp_" + std::string(buf, result.ptr);

        auto candidate = temp_root / name;

        // create_directory returns true only if it created the directory,
        // false (without setting ec) if it already existed, and sets ec on
        // a real error. This gives a race-free "did I create it" check.
        std::error_code ec;
        if (std::filesystem::create_directory(candidate, ec))
        {
            _path = std::move(candidate);
            return;
        }
        if (ec)
        {
            throw std::runtime_error(
                "cannot create temp directory in '" +
                temp_root.u8string() + "': " + ec.message());
        }

        // Name collided; loop and try another.
    }

    throw std::runtime_error(
        "cannot create a unique temp directory in '" +
        temp_root.u8string() + "'");
}

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
