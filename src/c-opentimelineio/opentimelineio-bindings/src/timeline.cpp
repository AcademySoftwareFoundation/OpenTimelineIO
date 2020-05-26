#include "copentimelineio/timeline.h"
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>
#include <vector>

typedef std::vector<OTIO_NS::Track*>           TrackVectorDef;
typedef std::vector<OTIO_NS::Track*>::iterator TrackVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    Timeline* Timeline_create(
        const char*    name,
        RationalTime*  global_start_time,
        AnyDictionary* metadata)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            nonstd::nullopt;
        if(global_start_time != NULL)
        {
            rationalTimeOptional = nonstd::optional<opentime::RationalTime>(
                *reinterpret_cast<opentime::RationalTime*>(global_start_time));
        }
        return reinterpret_cast<Timeline*>(new OTIO_NS::Timeline(
            name,
            rationalTimeOptional,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    Stack* Timeline_tracks(Timeline* self)
    {
        return reinterpret_cast<Stack*>(
            reinterpret_cast<OTIO_NS::Timeline*>(self)->tracks());
    }
    void Timeline_set_tracks(Timeline* self, Stack* stack)
    {
        reinterpret_cast<OTIO_NS::Timeline*>(self)->set_tracks(
            reinterpret_cast<OTIO_NS::Stack*>(stack));
    }
    RationalTime* Timeline_global_start_time(Timeline* self)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->global_start_time();
        if(rationalTimeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTimeOptional.value()));
    }
    void Timeline_set_global_start_time(
        Timeline* self, RationalTime* global_start_time)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            nonstd::nullopt;
        if(global_start_time != NULL)
        {
            rationalTimeOptional = nonstd::optional<opentime::RationalTime>(
                *reinterpret_cast<opentime::RationalTime*>(global_start_time));
        }
        reinterpret_cast<OTIO_NS::Timeline*>(self)->set_global_start_time(
            rationalTimeOptional);
    }
    RationalTime*
    Timeline_duration(Timeline* self, OTIOErrorStatus* error_status)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->duration(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    TimeRange* Timeline_range_of_child(
        Timeline* self, Composable* child, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->range_of_child(
                reinterpret_cast<OTIO_NS::Composable*>(child),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TrackVector* Timeline_audio_tracks(Timeline* self)
    {
        TrackVectorDef trackVector =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->audio_tracks();
        return reinterpret_cast<TrackVector*>(new TrackVectorDef(trackVector));
    }
    TrackVector* Timeline_video_tracks(Timeline* self)
    {
        TrackVectorDef trackVector =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->video_tracks();
        return reinterpret_cast<TrackVector*>(new TrackVectorDef(trackVector));
    }
#ifdef __cplusplus
}
#endif
