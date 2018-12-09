#pragma once

#include <pybind11/pybind11.h>
#include "opentimelineio/errorStatus.h"

struct ErrorStatusHandler {
    operator ErrorStatus* () {
        return &error_status;
    }
    
    ~ErrorStatusHandler() noexcept(false);

    ErrorStatus error_status;
};
