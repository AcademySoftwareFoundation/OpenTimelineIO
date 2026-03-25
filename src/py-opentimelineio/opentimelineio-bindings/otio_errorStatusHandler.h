// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <pybind11/pybind11.h>
#include "opentimelineio/errorStatus.h"

using namespace opentimelineio::OPENTIMELINEIO_VERSION_NS;

struct ErrorStatusHandler {
    operator ErrorStatus* () {
        return &error_status;
    }
    
    ~ErrorStatusHandler() noexcept(false);

    std::string details();
    std::string full_details();

    ErrorStatus error_status;
};
