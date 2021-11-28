#include "utils.h"

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

namespace {

Tests*
instance()
{
    static Tests* p = nullptr;
    if (!p)
    {
        p = new Tests;
    }
    return p;
}

} // namespace

void
Tests::run(int argc, char** argv)
{
    std::vector<std::string> filter;
    for (int arg = 1; arg < argc; ++arg)
    {
        filter.push_back(argv[arg]);
    }

    for (auto const& test: instance()->_tests)
    {
        bool run_test = true;
        if (!filter.empty())
        {
            const auto filter_it = std::find(
                filter.begin(), filter.end(), test.group + "/" + test.name);
            run_test = filter_it != filter.end();
        }
        if (run_test)
        {
            test.function();
        }
    }
}

Tests::AddTest::AddTest(
    std::string const& group,
    std::string const& name,
    std::function<void(void)> const& function)
{
    instance()->_tests.push_back({ group, name, function });
}
