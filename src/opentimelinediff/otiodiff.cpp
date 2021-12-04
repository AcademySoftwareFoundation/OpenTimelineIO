
#include "trackDiff.h"

#include <opentimelineio/stackAlgorithm.h>
#include <opentimelineio/timeline.h>

#include <iostream>
#include <sstream>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

void print_error(otio::ErrorStatus const& error_status)
{
    std::cout << "ERROR: " 
        << otio::ErrorStatus::outcome_to_string(error_status.outcome) << ": " 
        << error_status.details << std::endl;
}



int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "Usage: diff_video_track (prev_path) (new_path)"
                  << std::endl;
        return 1;
    }
    
    // Read the files
    otio::ErrorStatus error_status;
    otio::SerializableObject::Retainer<otio::Timeline> 
        prev_timeline(dynamic_cast<otio::Timeline*>(
                    otio::Timeline::from_json_file(argv[1], &error_status)));

    if (!prev_timeline)
    {
        print_error(error_status);
        return 1;
    }

    auto prev_video_tracks = prev_timeline.value->video_tracks();
     
    otio::SerializableObject::Retainer<otio::Timeline> 
        new_timeline(dynamic_cast<otio::Timeline*>(
                    otio::Timeline::from_json_file(argv[2], &error_status)));

    if (!new_timeline)
    {
        print_error(error_status);
        return 1;
    }

    auto new_video_tracks = new_timeline.value->video_tracks();
    
    std::cout << "Flattening " << prev_video_tracks.size() 
              << " video tracks into one..." << std::endl;

    auto flattened_prev_track = 
        otio::flatten_stack(prev_video_tracks, &error_status);

    if (!flattened_prev_track or is_error(error_status))
    {
        print_error(error_status);
        return 1;
    }

    std::cout << "Flattening " << new_video_tracks.size() 
              << " video tracks into one..." << std::endl;

    auto flattened_new_track = 
        otio::flatten_stack(new_video_tracks, &error_status);

    if (!flattened_new_track or is_error(error_status))
    {
        print_error(error_status);
        return 1;
    }
    
    otio::Stack* stack = otio::track_clip_visual_diff(
                                flattened_prev_track, flattened_new_track,
                                [](otio::Composable const*const a,
                                   otio::Composable const*const b) ->
                                        bool { return (a != nullptr) &&
                                               (b != nullptr) &&
                                               (a->name() == b->name()); });
    
    auto newtimeline = new otio::Timeline("diff");
    newtimeline->set_tracks(stack);
    if (!newtimeline->to_json_file("/var/tmp/diff.otio", &error_status))
    {
        print_error(error_status);
        return 1;
    }

    return 0;
}
