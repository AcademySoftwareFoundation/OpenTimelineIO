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

//
// {
//  "OTIO_CORE": {
//  ^ family
//      "0.14.0": {
//      ^ family_label
//          "Clip": 1,
//          ^ schema  ^ schema_version
//          ...
//      },
//      "0.15.0": {
//          ...
//      },
//      ...
//  },
//  "MY_COMPANY_PLUGIN_SETS": {}
// }


// typedefs for the schema downgrading system
using schema_version_map = std::unordered_map<std::string, int>;
using label_to_schema_version_map = std::unordered_map<std::string, schema_version_map>;
using family_to_label_map = std::unordered_map<std::string, label_to_schema_version_map>;
using family_label_spec = std::pair<std::string, std::string>;

/// add a new family:version:schema_version_map for downgrading
bool
add_family_label_version(
        const std::string& family, 
        const std::string& label,
        const schema_version_map& new_map,
        ErrorStatus* err
);

const family_to_label_map
family_label_version_map();

std::string 
serialize_json_to_string(
    const any& value,
    optional<family_label_spec> target_family_label_spec = {},
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
    optional<family_label_spec> target_family_label_spec = {},
    ErrorStatus*       error_status = nullptr,
    int                indent       = 4
);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
