#include "opentimelineio/errorStatus.h"

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
    default:
        return "unknown/illegal ErrorStatus::Outcomde code";
    };
}
