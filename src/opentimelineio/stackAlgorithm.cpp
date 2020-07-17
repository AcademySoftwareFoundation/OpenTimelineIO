#include "opentimelineio/stackAlgorithm.h"
#include "opentimelineio/trackAlgorithm.h"
#include "opentimelineio/track.h"
#include "opentimelineio/transition.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
typedef std::map<Track*, std::map<Composable*, TimeRange>> RangeTrackMap;

static void _flatten_next_item(RangeTrackMap& range_track_map, Track* flat_track,
                               std::vector<Track*> const& tracks,
                               int track_index, optional<TimeRange> trim_range,
                               ErrorStatus* error_status) {
    if (track_index < 0) {
        track_index = int(tracks.size()) - 1;
    }
    
    if (track_index < 0) {
        return;
    }
    
    Track* track = tracks[track_index];
    
    SerializableObject::Retainer<Track> track_retainer;
    if (trim_range) {
        track = track_trimmed_to_range(track, *trim_range, error_status);
        track_retainer = SerializableObject::Retainer<Track>(track);
    }
    
    std::map<Composable*, TimeRange>* track_map;
    auto it = range_track_map.find(track);
    if (it != range_track_map.end()) {
        track_map = &it->second;
    }
    else {
        auto result = range_track_map.emplace(track, track->range_of_all_children(error_status));
        if (*error_status) {
            return;
        }
        track_map = &result.first->second;
    }
    for (auto child: track->children()) {
        Item* item = dynamic_cast<Item*>(child.value);
        if (!item) {
            if (!dynamic_cast<Transition*>(child.value)) {
                *error_status = ErrorStatus(ErrorStatus::TYPE_MISMATCH,
                                            "expected item of type Item* or Transition*", child.value);
                return;
            }
        }
        
        if (!item || item->visible() || track_index == 0) {
            flat_track->insert_child(static_cast<int>(flat_track->children().size()),
                                     static_cast<Composable*>(child.value->clone(error_status)),
                                     error_status);
            if (*error_status) {
                return;
            }
        }
        else {
            TimeRange trim = (*track_map)[item];
            if (trim_range) {
                trim = TimeRange(trim.start_time() + trim_range->start_time(), trim.duration());
                (*track_map)[item] = trim;
            }
            
            _flatten_next_item(range_track_map, flat_track, tracks, track_index - 1, trim, error_status);
        }
    }

    // range_track_map persists over the entire duration of flatten_stack
    // track_retainer.value is about to be deleted; it's entirely possible
    // that a new item will be created at the same pointer location, so we
    // have to clean this value out of the map now.
    if (track_retainer.value) {
        range_track_map.erase(track_retainer.value);
    }
}

Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status) {
    std::vector<Track*> tracks;
    tracks.reserve(in_stack->children().size());
    
    for (auto c : in_stack->children()) {
        if (Track* track = dynamic_cast<Track*>(c.value)) {
            tracks.push_back(track);
        }
        else {
            *error_status = ErrorStatus(ErrorStatus::TYPE_MISMATCH,
                                        "expected item of type Track*", c);
            return nullptr;
        }
    }

    Track* flat_track = new Track;
    flat_track->set_name("Flattened");
    
    RangeTrackMap range_track_map;
    _flatten_next_item(range_track_map, flat_track, tracks, -1, nullopt, error_status);
    return flat_track;
}

Track* flatten_stack(std::vector<Track*> const& tracks, ErrorStatus* error_status) {
    Track* flat_track = new Track;
    flat_track->set_name("Flattened");
    
    RangeTrackMap range_track_map;
    _flatten_next_item(range_track_map, flat_track, tracks, -1, nullopt, error_status);
    return flat_track;
}
} }
