// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/any.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/version.h"
#include "opentimelineio/typeRegistry.h"
#include <opentimelineio/optional.h>

#include <string>
#include <unordered_map>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {


std::string 
serialize_json_to_string(
    const any& value,
    optional<const schema_version_map*> schema_version_targets = {},
    ErrorStatus* error_status = nullptr,
    int indent = 4
);

bool 
serialize_json_to_file(
    const any&         value,
    std::string const& file_name,
    // @TODO: I think this wants to be an optional<const family_label_spec&>, 
    //        but that isn't allowed, so maybe a const family_label_spec*?
    //        (to avoid the copy).
    //        these aren't inner loop functions, so isn't *that* crucial anyway.
    optional<const schema_version_map*> schema_version_targets = {},
    ErrorStatus*       error_status = nullptr,
    int                indent       = 4
);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
