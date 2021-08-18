#pragma once

#include "opentime/stringPrintf.h"
#include "opentimelineio/any.h"
#include "opentimelineio/version.h"
using opentime::string_printf;

#include <string>

namespace opentimelineio
{
namespace OPENTIMELINEIO_VERSION
{

void fatal_error(std::string const& errMsg);

std::string demangled_type_name(std::type_info const&);
std::string demangled_type_name(any const& a);
std::string demangled_type_name(class SerializableObject*);

template <typename T>
std::string
demangled_type_name()
{
    return demangled_type_name(typeid(T));
}

bool split_schema_string(
    std::string const& schema_and_version,
    std::string*       schema_name,
    int*               schema_version);

} // namespace OPENTIMELINEIO_VERSION
} // namespace opentimelineio
