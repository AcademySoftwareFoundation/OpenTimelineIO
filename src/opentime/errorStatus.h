#ifndef OPENTIME_ERROR_STATUSH
#define OPENTIME_ERROR_STATUSH

#include <string>

namespace opentime {
    
struct ErrorStatus {
    operator bool () {
        return outcome != Outcome::OK;
    }
    
    enum Outcome {
        OK,
        INVALID_TIMECODE_RATE,
        NON_DROPFRAME_RATE,
        INVALID_TIMECODE_STRING,
        INVALID_TIME_STRING,
        TIMECODE_RATE_MISMATCH,
        NEGATIVE_VALUE,
    };

    ErrorStatus() : outcome {OK} {}
    
    ErrorStatus(Outcome in_outcome) :
        outcome {in_outcome},
        details {outcome_to_string(in_outcome)} {}

    ErrorStatus(Outcome in_outcome, std::string const& in_details)
        : outcome {in_outcome},
          details {in_details} {}
    
    Outcome outcome;
    std::string details;

    static std::string outcome_to_string(Outcome);
};

}

#endif
