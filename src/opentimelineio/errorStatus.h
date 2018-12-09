#ifndef OTIO_ERROR_STATUSH
#define OTIO_ERROR_STATUSH

#include <string>

struct ErrorStatus {
    operator bool () {
        return outcome != Outcome::OK;
    }
    
    enum Outcome {
        OK,
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
        INTERNAL_ERROR
    };

    ErrorStatus()
        : outcome(OK) {
    }
    
    ErrorStatus(Outcome in_outcome)
        : outcome(in_outcome),
          details(outcome_to_string(in_outcome)),
          full_description(details) {
    }

    ErrorStatus(Outcome in_outcome, std::string const& in_details)
        : outcome(in_outcome),
          details(in_details),
          full_description(outcome_to_string(in_outcome) + ": " + in_details) {
    }

    ErrorStatus& operator=(Outcome outcome) {
        *this = ErrorStatus(outcome);
        return *this;
    }

    Outcome outcome;
    std::string details;
    std::string full_description;

    static std::string outcome_to_string(Outcome);
};

#endif

    
    
    
    
