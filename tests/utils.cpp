// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <iostream>
#include <memory>

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
