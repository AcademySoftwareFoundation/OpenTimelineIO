#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct ErrorStatus;
    typedef struct ErrorStatus ErrorStatus;

    typedef enum
    {
        OTIO_ErrorStatus_Outcome_OK                                   = 0,
        OTIO_ErrorStatus_Outcome_INVALID_TIMECODE_RATE                = 1,
        OTIO_ErrorStatus_Outcome_NON_DROPFRAME_RATE                   = 2,
        OTIO_ErrorStatus_Outcome_INVALID_TIMECODE_STRING              = 3,
        OTIO_ErrorStatus_Outcome_INVALID_TIME_STRING                  = 4,
        OTIO_ErrorStatus_Outcome_TIMECODE_RATE_MISMATCH               = 5,
        OTIO_ErrorStatus_Outcome_NEGATIVE_VALUE                       = 6,
        OTIO_ErrorStatus_Outcome_INVALID_RATE_FOR_DROP_FRAME_TIMECODE = 7,
    } OTIO_ErrorStatus_Outcome_;
    typedef int  OTIO_ErrorStatus_Outcome;
    ErrorStatus* ErrorStatus_create();
    ErrorStatus*
                 ErrorStatus_create_with_outcome(OTIO_ErrorStatus_Outcome in_outcome);
    ErrorStatus* ErrorStatus_create_with_outcome_and_details(
        OTIO_ErrorStatus_Outcome in_outcome, const char* in_details);
    const char* ErrorStatus_outcome_to_string(
        ErrorStatus* self, OTIO_ErrorStatus_Outcome var1);
    void ErrorStatus_destroy(ErrorStatus* self);
#ifdef __cplusplus
}
#endif
