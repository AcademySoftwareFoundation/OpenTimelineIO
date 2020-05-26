#include "copentimelineio/trackAlgorithm.h"
#include <opentime/timeRange.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/track.h>
#include <opentimelineio/trackAlgorithm.h>

#ifdef __cplusplus
extern "C"
{
#endif

    Track* track_trimmed_to_range(
        Track* in_track, TimeRange* trim_range, OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<Track*>(OTIO_NS::track_trimmed_to_range(
            reinterpret_cast<OTIO_NS::Track*>(in_track),
            *reinterpret_cast<opentime::TimeRange*>(trim_range),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status)));
    }

#ifdef __cplusplus
}
#endif