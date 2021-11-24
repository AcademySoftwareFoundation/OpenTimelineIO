#pragma once

#include "opentimelineio/any.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

bool deserialize_json_from_string(
    std::string const& input,
    any*               destination,
    ErrorStatus*       error_status = nullptr);

bool deserialize_json_from_file(
    std::string const& file_name,
    any*               destination,
    ErrorStatus*       error_status = nullptr);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
