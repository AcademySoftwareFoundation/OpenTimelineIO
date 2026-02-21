// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

class SerializableObject;

/// @brief This struct represents the return status of a function.
struct OTIO_API_TYPE ErrorStatus
{
    /// @brief This enumeration represents the possible outcomes.
    enum Outcome
    {
        OK = 0,
        NOT_IMPLEMENTED,
        UNRESOLVED_OBJECT_REFERENCE,
        DUPLICATE_OBJECT_REFERENCE,
        MALFORMED_SCHEMA,
        JSON_PARSE_ERROR,
        CHILD_ALREADY_PARENTED,
        FILE_OPEN_FAILED,
        FILE_WRITE_FAILED,
        SCHEMA_ALREADY_REGISTERED,
        SCHEMA_NOT_REGISTERED,
        SCHEMA_VERSION_UNSUPPORTED,
        KEY_NOT_FOUND,
        ILLEGAL_INDEX,
        TYPE_MISMATCH,
        INTERNAL_ERROR,
        NOT_AN_ITEM,
        NOT_A_CHILD_OF,
        NOT_A_CHILD,
        NOT_DESCENDED_FROM,
        CANNOT_COMPUTE_AVAILABLE_RANGE,
        INVALID_TIME_RANGE,
        OBJECT_WITHOUT_DURATION,
        CANNOT_TRIM_TRANSITION,
        OBJECT_CYCLE,
        CANNOT_COMPUTE_BOUNDS,
        MEDIA_REFERENCES_DO_NOT_CONTAIN_ACTIVE_KEY,
        MEDIA_REFERENCES_CONTAIN_EMPTY_KEY,
        NOT_A_GAP,
        BUNDLE_SIZE_ERROR,
        BUNDLE_WRITE_ERROR,
        BUNDLE_READ_ERROR
    };

    /// @brief Construct a new status with no error.
    ErrorStatus()
        : outcome(OK)
        , object_details(nullptr)
    {}

    /// @brief Construct a new status with the given outcome.
    ErrorStatus(Outcome in_outcome)
        : outcome(in_outcome)
        , details(outcome_to_string(in_outcome))
        , full_description(details)
        , object_details(nullptr)
    {}

    /// @brief Construct a new status with the given outcome, details, and object.
    ErrorStatus(
        Outcome                   in_outcome,
        std::string const&        in_details,
        SerializableObject const* object = nullptr)
        : outcome(in_outcome)
        , details(in_details)
        , full_description(outcome_to_string(in_outcome) + ": " + in_details)
        , object_details(object)
    {}

    /// @brief Copy operator.
    ErrorStatus& operator=(Outcome in_outcome)
    {
        *this = ErrorStatus(in_outcome);
        return *this;
    }

    /// @brief The outcome of the function.
    Outcome outcome;

    /// @brief A human readable string that provides details about the outcome.
    std::string details;

    /// @brief A human readable string that provides the full description of the status.
    std::string full_description;

    /// @brief The object related to the status.
    SerializableObject const* object_details;

    //! @brief Return a human readable string for the given outcome.
    static OTIO_API std::string outcome_to_string(Outcome);
};

/// @brief Check whether the given ErrorStatus is an error.
OTIO_API constexpr bool
is_error(const ErrorStatus& es) noexcept
{
    return ErrorStatus::Outcome::OK != es.outcome;
}

/// @brief Check whether the given ErrorStatus* is non-null and an error.
OTIO_API constexpr bool
is_error(const ErrorStatus* es) noexcept
{
    return es && ErrorStatus::Outcome::OK != es->outcome;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
