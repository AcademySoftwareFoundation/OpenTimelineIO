// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/export.h"
#include "opentime/version.h"
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

/// @brief This struct represents the return status of a function.
struct OPENTIME_EXPORT ErrorStatus
{
    /// @brief This enumeration represents the possible outcomes.
    enum Outcome
    {
        OK = 0,
        INVALID_TIMECODE_RATE,
        INVALID_TIMECODE_STRING,
        INVALID_TIME_STRING,
        TIMECODE_RATE_MISMATCH,
        NEGATIVE_VALUE,
        INVALID_RATE_FOR_DROP_FRAME_TIMECODE,
    };

    /// @brief Construct a new status with no error.
    ErrorStatus()
        : outcome{ OK }
    {}

    /// @brief Construct a new status with the given outcome.
    ErrorStatus(Outcome in_outcome)
        : outcome{ in_outcome }
        , details{ outcome_to_string(in_outcome) }
    {}

    /// @brief Construct a new status with the given outcome and details.
    ErrorStatus(Outcome in_outcome, std::string const& in_details)
        : outcome{ in_outcome }
        , details{ in_details }
    {}

    /// @brief The outcome of the function.
    Outcome outcome;

    /// @brief A human readable string that provides details about the outcome.
    std::string details;

    ///! @brief Return a human readable string for the given outcome.
    static std::string outcome_to_string(Outcome);
};

///! @brief Check whether the given ErrorStatus is an error.
OPENTIME_EXPORT constexpr bool
is_error(const ErrorStatus& es) noexcept
{
    return ErrorStatus::Outcome::OK != es.outcome;
}

///! @brief Check whether the given ErrorStatus is non-null and an error.
OPENTIME_EXPORT constexpr bool
is_error(const ErrorStatus* es) noexcept
{
    return es && ErrorStatus::Outcome::OK != es->outcome;
}

}} // namespace opentime::OPENTIME_VERSION
