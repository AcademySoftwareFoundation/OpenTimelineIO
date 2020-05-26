#pragma once

#include "copentime/timeRange.h"
#include "errorStatus.h"
#include "track.h"

#ifdef __cplusplus
extern "C"
{
#endif

    Track* track_trimmed_to_range(
        Track* in_track, TimeRange* trim_range, OTIOErrorStatus* error_status);

#ifdef __cplusplus
}
#endif