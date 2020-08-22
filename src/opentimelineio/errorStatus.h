#pragma once

#include "opentimelineio/version.h"
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class SerializableObject;

struct ErrorStatus {
    operator bool () {
        return outcome != Outcome::OK;
    }
    
    enum Outcome {
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
        CANNOT_TRIM_TRANSITION
    };

    ErrorStatus()
        : outcome(OK),
          object_details(nullptr) {
    }
    
    ErrorStatus(Outcome in_outcome)
        : outcome(in_outcome),
          details(outcome_to_string(in_outcome)),
          full_description(details),
          object_details(nullptr) {
    }
    
    ErrorStatus(Outcome in_outcome, std::string const& in_details,
                SerializableObject const* object = nullptr)
        : outcome(in_outcome),
          details(in_details),
          full_description(outcome_to_string(in_outcome) + ": " + in_details),
          object_details(object) {
    }
    
    ErrorStatus& operator=(Outcome in_outcome) {
        *this = ErrorStatus(in_outcome);
        return *this;
    }

    Outcome outcome;
    std::string details;
    std::string full_description;
    SerializableObject const* object_details;

    static std::string outcome_to_string(Outcome);
};

} }
