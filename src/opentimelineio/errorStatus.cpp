#include "opentimelineio/errorStatus.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
std::string ErrorStatus::outcome_to_string(Outcome o) {
    switch(o) {
    case OK:
        return std::string();
    case NOT_IMPLEMENTED:
        return "method not implemented for this class";
    case UNRESOLVED_OBJECT_REFERENCE:
        return "unresolved object reference encountered";
    case DUPLICATE_OBJECT_REFERENCE:
        return "duplicate object reference encountered";
    case MALFORMED_SCHEMA:
        return "schema specifier is malformed/illegal";
    case JSON_PARSE_ERROR:
        return "JSON parse error";
    case CHILD_ALREADY_PARENTED:
        return "child already has a parent";
    case FILE_OPEN_FAILED:
        return "failed to open file for reading";
    case FILE_WRITE_FAILED:
        return "failed to open file for writing";
    case SCHEMA_ALREADY_REGISTERED:
        return "schema has already been registered";
    case SCHEMA_NOT_REGISTERED:
        return "schema is not registered/known";
    case KEY_NOT_FOUND:
        return "key not present reading from dictionary";
    case ILLEGAL_INDEX:
        return "illegal index";
    case TYPE_MISMATCH:
        return "type mismatch while decoding";
    case INTERNAL_ERROR:
        return "internal error (aka \"this code has a bug\")";
    case NOT_DESCENDED_FROM:
        return "item is not a descendent of specified object";
    case NOT_A_CHILD_OF:
        return "item is not a child of specified object";
    case NOT_AN_ITEM:
        return "object is not descendent of Item type";
    case SCHEMA_VERSION_UNSUPPORTED:
        return "unsupported schema version";
    case NOT_A_CHILD:
        return "item has no parent";
    case CANNOT_COMPUTE_AVAILABLE_RANGE:
        return "Cannot compute available range";
    case INVALID_TIME_RANGE:
        return "computed time range would be invalid";
    case OBJECT_WITHOUT_DURATION:
        return "cannot compute duration on this type of object";
    case CANNOT_TRIM_TRANSITION:
        return "cannot trim transition";
    case INSTANCING_NOT_SUPPORTED:
        return "cannot serialize object with cycles unless built with OTIO_INSTANCING_SUPPORT";
    default:
        return "unknown/illegal ErrorStatus::Outcome code";
    };
}

} }
