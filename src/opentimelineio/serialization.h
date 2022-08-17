// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/any.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/version.h"
#include <opentimelineio/optional.h>

#include <string>
#include <unordered_map>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {


// a mapping of schema name : schema version
using schema_version_map = std::unordered_map<std::string, int>;
const static schema_version_map EMPTY_VERSION_MAP = schema_version_map();

std::string 
serialize_json_to_string(
    const any& value,
    optional<const schema_version_map*> downgrade_version_manifest = {},
    ErrorStatus* error_status = nullptr,
    int indent = 4
);

bool 
serialize_json_to_file(
    const any&         value,
    std::string const& file_name,
    optional<const schema_version_map*> downgrade_version_manifest = {},
    ErrorStatus*       error_status = nullptr,
    int                indent       = 4
);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
