#pragma once

#include "opentime/version.h"
#include <string>

namespace opentime { namespace OPENTIME_VERSION  {
    
struct ErrorStatus {
    operator bool () {
        return outcome != Outcome::OK;
    }
    
    enum Outcome {
        OK = 0,
        INVALID_TIMECODE_RATE,
        NON_DROPFRAME_RATE,
        INVALID_TIMECODE_STRING,
        INVALID_TIME_STRING,
        TIMECODE_RATE_MISMATCH,
        NEGATIVE_VALUE,
        INVALID_RATE_FOR_DROP_FRAME_TIMECODE,
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

} }
