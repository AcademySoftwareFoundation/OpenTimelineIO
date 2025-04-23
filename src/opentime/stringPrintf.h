// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/version.h"
#include <cstdio>
#include <memory>
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

/// @brief This provides printf style functionality for std::string.
template <typename... Args>
std::string
string_printf(char const* format, Args... args)
{
    char   buffer[4096];
    size_t size = snprintf(buffer, sizeof(buffer), format, args...) + 1;
    if (size < sizeof(buffer))
    {
        return std::string(buffer);
    }

    std::unique_ptr<char[]> buf(new char[size]);
    std::snprintf(buf.get(), size, format, args...);
    return std::string(buf.get());
}

}} // namespace opentime::OPENTIME_VERSION
