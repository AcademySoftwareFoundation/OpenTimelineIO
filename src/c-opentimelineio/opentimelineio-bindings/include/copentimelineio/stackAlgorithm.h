#pragma once

#include "errorStatus.h"
#include "stack.h"
#include "track.h"
#include "trackVector.h"

#ifdef __cplusplus
extern "C"
{
#endif

    Track* flatten_stack(Stack* in_stack, OTIOErrorStatus* error_status);
    Track* flatten_stack_track_vector(
        TrackVector* tracks, OTIOErrorStatus* error_status);

#ifdef __cplusplus
}
#endif