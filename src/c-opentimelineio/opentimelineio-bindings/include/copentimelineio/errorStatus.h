#pragma once

#include "serializableObject.h"

#ifdef __cplusplus
extern "C"
{
#endif
    struct OTIOErrorStatus;
    typedef struct OTIOErrorStatus OTIOErrorStatus;
    struct SerializableObject;
    typedef struct SerializableObject SerializableObject;

    typedef enum
    {
        OTIO_ErrorStatus_Outcome_OK                             = 0,
        OTIO_ErrorStatus_Outcome_NOT_IMPLEMENTED                = 1,
        OTIO_ErrorStatus_Outcome_UNRESOLVED_OBJECT_REFERENCE    = 2,
        OTIO_ErrorStatus_Outcome_DUPLICATE_OBJECT_REFERENCE     = 3,
        OTIO_ErrorStatus_Outcome_MALFORMED_SCHEMA               = 4,
        OTIO_ErrorStatus_Outcome_JSON_PARSE_ERROR               = 5,
        OTIO_ErrorStatus_Outcome_CHILD_ALREADY_PARENTED         = 6,
        OTIO_ErrorStatus_Outcome_FILE_OPEN_FAILED               = 7,
        OTIO_ErrorStatus_Outcome_FILE_WRITE_FAILED              = 8,
        OTIO_ErrorStatus_Outcome_SCHEMA_ALREADY_REGISTERED      = 9,
        OTIO_ErrorStatus_Outcome_SCHEMA_NOT_REGISTERED          = 10,
        OTIO_ErrorStatus_Outcome_SCHEMA_VERSION_UNSUPPORTED     = 11,
        OTIO_ErrorStatus_Outcome_KEY_NOT_FOUND                  = 12,
        OTIO_ErrorStatus_Outcome_ILLEGAL_INDEX                  = 13,
        OTIO_ErrorStatus_Outcome_TYPE_MISMATCH                  = 14,
        OTIO_ErrorStatus_Outcome_INTERNAL_ERROR                 = 15,
        OTIO_ErrorStatus_Outcome_NOT_AN_ITEM                    = 16,
        OTIO_ErrorStatus_Outcome_NOT_A_CHILD_OF                 = 17,
        OTIO_ErrorStatus_Outcome_NOT_A_CHILD                    = 18,
        OTIO_ErrorStatus_Outcome_NOT_DESCENDED_FROM             = 19,
        OTIO_ErrorStatus_Outcome_CANNOT_COMPUTE_AVAILABLE_RANGE = 20,
        OTIO_ErrorStatus_Outcome_INVALID_TIME_RANGE             = 21,
        OTIO_ErrorStatus_Outcome_OBJECT_WITHOUT_DURATION        = 22,
        OTIO_ErrorStatus_Outcome_CANNOT_TRIM_TRANSITION         = 23,
    } OTIO_ErrorStatus_Outcome_;
    typedef int      OTIO_ErrorStatus_Outcome;
    OTIOErrorStatus* OTIOErrorStatus_create();
    OTIOErrorStatus*
    OTIOErrorStatus_create_with_outcome(OTIO_ErrorStatus_Outcome in_outcome);
    OTIOErrorStatus*
    OTIOErrorStatus_create_with_outcome_details_serializable_object(
        OTIO_ErrorStatus_Outcome in_outcome,
        const char*              in_details,
        SerializableObject*      object);
    const char* OTIOErrorStatus_outcome_to_string(
        OTIOErrorStatus* self, OTIO_ErrorStatus_Outcome var1);
    void OTIOErrorStatus_destroy(OTIOErrorStatus* self);
#ifdef __cplusplus
}
#endif