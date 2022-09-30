// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/any.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/version.h"
#include <opentimelineio/optional.h>

#include <string>
#include <unordered_map>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

std::string serialize_json_to_string(
    const any&                value,
    const schema_version_map* schema_version_targets = nullptr,
    ErrorStatus*              error_status           = nullptr,
    int                       indent                 = 4);

bool serialize_json_to_file(
    const any&                value,
    std::string const&        file_name,
    const schema_version_map* schema_version_targets = nullptr,
    ErrorStatus*              error_status           = nullptr,
    int                       indent                 = 4);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
