// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/serializableObject.h"
#if defined(__GNUC__) || defined(__clang__)
#    include <cstdlib>
#    include <cxxabi.h>
#    include <memory>
#else
#    include <typeinfo>
#endif

namespace {
#if defined(__GNUC__) || defined(__clang__)
std::string
cxxabi_type_name_for_error_mesage(const char* name)
{
    int status = -4; // some arbitrary value to eliminate the compiler warning

    std::unique_ptr<char, void (*)(void*)> res{
        abi::__cxa_demangle(name, NULL, NULL, &status),
        std::free
    };

    return (status == 0) ? res.get() : name;
}
#endif
} // namespace

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

std::string
type_name_for_error_message(std::type_info const& t)
{
    if (t == typeid(std::string))
    {
        return "string";
    }
    if (t == typeid(void))
    {
        return "None";
    }

#if defined(__GNUC__) || defined(__clang__)
    return ::cxxabi_type_name_for_error_mesage(t.name());
#else
    // On Windows std::type_info.name() returns a human readable string.
    return t.name();
#endif
}

std::string
type_name_for_error_message(any const& a)
{
    return type_name_for_error_message(a.type());
}

std::string
type_name_for_error_message(SerializableObject* so)
{
    return type_name_for_error_message(typeid(*so));
}

void
fatal_error(std::string const& errMsg)
{
    fprintf(stderr, "Fatal error: %s\n", errMsg.c_str());
    exit(-1);
}

bool
split_schema_string(
    std::string const& schema_and_version,
    std::string*       schema_name,
    int*               schema_version)
{
    size_t index = schema_and_version.rfind('.');
    if (index == std::string::npos)
    {
        return false;
    }

    *schema_name = schema_and_version.substr(0, index);
    try
    {
        *schema_version = std::stoi(schema_and_version.substr(index + 1));
        return true;
    }
    catch (...)
    {
        return false;
    }
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
