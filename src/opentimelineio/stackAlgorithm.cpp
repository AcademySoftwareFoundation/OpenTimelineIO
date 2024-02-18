// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/stackAlgorithm.h"
#include "opentimelineio/track.h"
#include "opentimelineio/trackAlgorithm.h"
#include "opentimelineio/transition.h"
#include "opentimelineio/gap.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

typedef std::map<Track*, std::map<Composable*, TimeRange>> RangeTrackMap;
typedef std::vector<SerializableObject::Retainer<Track>> TrackRetainerVector;

static void
_flatten_next_item(
    RangeTrackMap&             range_track_map,
    Track*                     flat_track,
    std::vector<Track*> const& tracks,
    int                        track_index,
    optional<TimeRange>        trim_range,
    ErrorStatus*               error_status)
{
    if (track_index < 0)
    {
        track_index = int(tracks.size()) - 1;
    }

    if (track_index < 0)
    {
        return;
    }

    Track* track = tracks[track_index];

    SerializableObject::Retainer<Track> track_retainer;
    if (trim_range)
    {
        track = track_trimmed_to_range(track, *trim_range, error_status);
        if (track == nullptr || is_error(error_status))
        {
            return;
        }
        track_retainer = SerializableObject::Retainer<Track>(track);
    }

    std::map<Composable*, TimeRange>* track_map;
    auto                              it = range_track_map.find(track);
    if (it != range_track_map.end())
    {
        track_map = &it->second;
    }
    else
    {
        auto result = range_track_map.emplace(
            track,
            track->range_of_all_children(error_status));
        if (is_error(error_status))
        {
            return;
        }
        track_map = &result.first->second;
    }
    for (auto child: track->children())
    {
        auto item = dynamic_retainer_cast<Item>(child);
        if (!item)
        {
            if (!dynamic_retainer_cast<Transition>(child))
            {
                if (error_status)
                {
                    *error_status = ErrorStatus(
                        ErrorStatus::TYPE_MISMATCH,
                        "expected item of type Item* || Transition*",
                        child);
                }
                return;
            }
        }

        if (!item || item->visible() || track_index == 0)
        {
            flat_track->insert_child(
                static_cast<int>(flat_track->children().size()),
                static_cast<Composable*>(child->clone(error_status)),
                error_status);
            if (is_error(error_status))
            {
                return;
            }
        }
        else
        {
            TimeRange trim = (*track_map)[item];
            if (trim_range)
            {
                trim = TimeRange(
                    trim.start_time() + trim_range->start_time(),
                    trim.duration());
                (*track_map)[item] = trim;
            }

            _flatten_next_item(
                range_track_map,
                flat_track,
                tracks,
                track_index - 1,
                trim,
                error_status);
            if (track == nullptr || is_error(error_status))
            {
                return;
            }
        }
    }

    // range_track_map persists over the entire duration of flatten_stack
    // track_retainer.value is about to be deleted; it's entirely possible
    // that a new item will be created at the same pointer location, so we
    // have to clean this value out of the map now.
    if (track_retainer)
    {
        range_track_map.erase(track_retainer);
    }
}

// make all tracks the same length by adding a gap to the end if they are shorter
static void
_normalize_tracks_lengths(std::vector<Track*>& tracks,
                          TrackRetainerVector& tracks_retainer,
                          ErrorStatus*         error_status)
{
    RationalTime duration;
    for (auto track: tracks)
    {
        duration = std::max(duration, track->duration(error_status));
        if (is_error(error_status))
        {
            return;
        }
    }

    for(int i = 0; i < tracks.size(); i++)
    {
        Track *track = tracks[i];
        RationalTime track_duration = track->duration(error_status);
        if (track_duration < duration)
        {
            track = static_cast<Track*>(track->clone(error_status));
            if (is_error(error_status))
            {
                return;
            }
            tracks_retainer.push_back(SerializableObject::Retainer<Track>(track));
            track->append_child(new Gap(duration - track_duration), error_status);
            if (is_error(error_status))
            {
                return;
            }
            tracks[i] = track;
        }
    }
}

Track*
flatten_stack(Stack* in_stack, ErrorStatus* error_status)
{
    std::vector<Track*> tracks;
    TrackRetainerVector tracks_retainer;
    tracks.reserve(in_stack->children().size());

    for (auto c: in_stack->children())
    {
        if (auto track = dynamic_retainer_cast<Track>(c))
        {
            if (track->enabled())
            {
                tracks.push_back(track);
            }
        }
        else
        {
            if (error_status)
            {
                *error_status = ErrorStatus(
                    ErrorStatus::TYPE_MISMATCH,
                    "expected item of type Track*",
                    c);
            }
            return nullptr;
        }
    }

    _normalize_tracks_lengths(tracks, tracks_retainer, error_status);
    if (is_error(error_status))
    {
        return nullptr;
    }

    Track* flat_track = new Track;
    flat_track->set_name("Flattened");

    RangeTrackMap range_track_map;
    _flatten_next_item(
        range_track_map,
        flat_track,
        tracks,
        -1,
        nullopt,
        error_status);
    return flat_track;
}

Track*
flatten_stack(std::vector<Track*> const& tracks, ErrorStatus* error_status)
{
    std::vector<Track*> flat_tracks;
    TrackRetainerVector tracks_retainer;
    flat_tracks.reserve(tracks.size());
    for (auto track : tracks)
    {
        flat_tracks.push_back(track);
    }

    _normalize_tracks_lengths(flat_tracks, tracks_retainer, error_status);
    if (is_error(error_status))
    {
        return nullptr;
    }

    Track* flat_track = new Track;
    flat_track->set_name("Flattened");

    RangeTrackMap range_track_map;
    _flatten_next_item(
        range_track_map,
        flat_track,
        flat_tracks,
        -1,
        nullopt,
        error_status);
    return flat_track;
}
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
