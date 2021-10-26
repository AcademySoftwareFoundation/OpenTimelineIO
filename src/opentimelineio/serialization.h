#pragma once

#include "opentimelineio/any.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/version.h"

#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

std::string serialize_json_to_string(
    const any& value, ErrorStatus* error_status = nullptr, int indent = 4);

bool serialize_json_to_file(
    const any&         value,
    std::string const& file_name,
    ErrorStatus*       error_status = nullptr,
    int                indent       = 4);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
