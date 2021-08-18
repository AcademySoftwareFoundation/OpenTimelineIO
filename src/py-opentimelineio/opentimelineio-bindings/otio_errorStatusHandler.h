#pragma once

#include "opentimelineio/errorStatus.h"
#include <pybind11/pybind11.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

struct ErrorStatusHandler
{
    operator ErrorStatus*() { return &error_status; }

    ~ErrorStatusHandler() noexcept(false);

    std::string details();
    std::string full_details();

    ErrorStatus error_status;
};
