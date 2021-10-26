#pragma once

#include "opentime/version.h"
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

struct ErrorStatus
{
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

    ErrorStatus()
        : outcome{ OK }
    {}

    ErrorStatus(Outcome in_outcome)
        : outcome{ in_outcome }
        , details{ outcome_to_string(in_outcome) }
    {}

    ErrorStatus(Outcome in_outcome, std::string const& in_details)
        : outcome{ in_outcome }
        , details{ in_details }
    {}

    Outcome     outcome;
    std::string details;

    static std::string outcome_to_string(Outcome);
};

// Check whether the given ErrorStatus is an error.
constexpr bool
is_error(const ErrorStatus& es) noexcept
{
    return ErrorStatus::Outcome::OK != es.outcome;
}

// Check whether the given ErrorStatus is non-null and an error.
constexpr bool
is_error(const ErrorStatus* es) noexcept
{
    return es && ErrorStatus::Outcome::OK != es->outcome;
}

}} // namespace opentime::OPENTIME_VERSION
