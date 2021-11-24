#include "opentime/errorStatus.h"

namespace opentime { namespace OPENTIME_VERSION {

std::string
ErrorStatus::outcome_to_string(Outcome o)
{
    switch (o)
    {
        case OK:
            return std::string();
        case INVALID_TIMECODE_RATE:
            return "invalid timecode rate";
        case INVALID_TIMECODE_STRING:
            return "string is not a valid timecode string";
        case TIMECODE_RATE_MISMATCH:
            return "timecode specifies a frame higher than its rate";
        case INVALID_TIME_STRING:
            return "invalid time string";
        case NEGATIVE_VALUE:
            return "value cannot be negative here";
        case INVALID_RATE_FOR_DROP_FRAME_TIMECODE:
            return "rate is not valid for drop frame timecode";
        default:
            return "unknown/illegal ErrorStatus::Outcome code";
    };
}

}} // namespace opentime::OPENTIME_VERSION
