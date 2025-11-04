// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/errorStatus.h"
#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/version.h"

#include <any>
#include <string>
#include <unordered_map>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Serialize JSON data to a string.
OTIO_API std::string serialize_json_to_string(
    const std::any&           value,
    const schema_version_map* schema_version_targets = nullptr,
    ErrorStatus*              error_status           = nullptr,
    int                       indent                 = 4);

/// @brief Serialize JSON data to a file.
OTIO_API bool serialize_json_to_file(
    const std::any&           value,
    std::string const&        file_name,
    const schema_version_map* schema_version_targets = nullptr,
    ErrorStatus*              error_status           = nullptr,
    int                       indent                 = 4);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
