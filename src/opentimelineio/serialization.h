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

static family_to_label_map FAMILY_LABEL_MAP {
    { 
        "OTIO_CORE", 
            { 
                { "test", 
                    { 
                        { "Clip", 1 } 
                    } 
                } 
            } 
    }
};


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
