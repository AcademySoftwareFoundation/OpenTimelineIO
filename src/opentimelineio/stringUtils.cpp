// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/serializableObject.h"
#include <cstdlib>
#include <memory>
#include <typeinfo>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

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

    return t.name();
}

std::string
type_name_for_error_message(std::any const& a)
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

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
