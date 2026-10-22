// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/stringPrintf.h"
#include "opentimelineio/export.h"
#include "opentimelineio/version.h"
using opentime::string_printf;

#include <any>
#include <filesystem>
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @name String Utilities
///@{

void fatal_error(std::string const& errMsg);

OTIO_API std::string type_name_for_error_message(std::type_info const&);
OTIO_API std::string type_name_for_error_message(std::any const& a);
OTIO_API std::string type_name_for_error_message(class SerializableObject*);

template <typename T>
std::string
type_name_for_error_message()
{
    return type_name_for_error_message(typeid(T));
}

bool split_schema_string(
    std::string const& schema_and_version,
    std::string*       schema_name,
    int*               schema_version);

///@}

/// @name Path Utilities
///
/// Paths are passed as UTF-8 strings. These convert between them and
/// std::filesystem::path the same way in C++17 and C++20, where
/// path::u8string() returns std::u8string rather than std::string.
///@{

/// Convert a UTF-8 string to a path.
inline std::filesystem::path
from_utf8(std::string const& value)
{
#if defined(__cpp_lib_char8_t)
    return std::filesystem::path(std::u8string(value.begin(), value.end()));
#else
    return std::filesystem::u8path(value);
#endif
}

/// Convert a path to a UTF-8 string.
inline std::string
to_utf8(std::filesystem::path const& value)
{
#if defined(__cpp_lib_char8_t)
    auto const out = value.u8string();
    return std::string(out.begin(), out.end());
#else
    return value.u8string();
#endif
}

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
