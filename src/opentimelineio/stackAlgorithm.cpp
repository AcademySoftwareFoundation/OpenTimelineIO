#include "opentimelineio/stackAlgorithm.h"
#include "opentimelineio/trackAlgorithm.h"
#include "opentimelineio/track.h"
#include "opentimelineio/transition.h"

typedef std::map<Track*, std::map<Composable*, TimeRange>> RangeTrackMap;

static void _flatten_next_item(RangeTrackMap& range_track_map, Track* flat_track,
                               Stack* in_stack, int track_index, optional<TimeRange> trim_range,
                               ErrorStatus* error_status) {
    if (track_index < 0) {
        track_index = int(in_stack->children().size()) - 1;
    }
    
    if (track_index < 0) {
        return;
    }
    
    Composable* c = in_stack->children()[track_index];
    Track* track = dynamic_cast<Track*>(c);
    if (!track) {
        *error_status = ErrorStatus(ErrorStatus::TYPE_MISMATCH,
                                    "expected item of type Track*", c);
        return;
    }
    
    SerializableObject::Retainer<> track_retainer;
    if (trim_range) {
        track = track_trimmed_to_range(track, *trim_range, error_status);
        track_retainer = SerializableObject::Retainer<>(track);
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
            *error_status = ErrorStatus(ErrorStatus::TYPE_MISMATCH,
                                        "expected item of type Item*", child.value);
            return;
        }
        
        if (item->visible() || track_index == 0 || dynamic_cast<Transition*>(item)) {
            flat_track->insert_child(flat_track->children().size(), static_cast<Composable*>(item->clone(error_status)),
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
            
            _flatten_next_item(range_track_map, flat_track, in_stack, track_index - 1, trim, error_status);
        }
    }
}

Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status) {
    Track* flat_track = new Track;
    flat_track->set_name("Flattened");
    
    RangeTrackMap range_track_map;
    _flatten_next_item(range_track_map, flat_track, in_stack, -1, nullopt, error_status);
    return flat_track;
}
