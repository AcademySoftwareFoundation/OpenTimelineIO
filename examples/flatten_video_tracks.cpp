#include "util.h"

#include <opentimelineio/stackAlgorithm.h>
#include <opentimelineio/timeline.h>

#include <iostream>
#include <sstream>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "Usage: flatten_video_tracks (inputpath) (outputpath)" << std::endl;
        return 1;
    }
    
    // Read the file
    otio::ErrorStatus error_status;
    otio::SerializableObject::Retainer<otio::Timeline> timeline(dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(argv[1], &error_status)));
    if (!timeline)
    {
        print_error(error_status);
        return 1;
    }
    auto video_tracks = timeline.value->video_tracks();
    auto audio_tracks = timeline.value->audio_tracks();
    
    std::cout << "Read " << video_tracks.size() << " video tracks and " <<
        audio_tracks.size() << " audio tracks." << std::endl;

    // Take just the video tracks - and flatten them into one.
    // This will trim away any overlapping segments, collapsing everything
    // into a single track.
    std::cout << "Flattening " << video_tracks.size() << " video tracks into one..." << std::endl;
    auto onetrack = otio::flatten_stack(video_tracks, &error_status);
    if (!onetrack)
    {
        print_error(error_status);
        return 1;
    }

    // Now make a new empty Timeline and put that one Track into it
    std::string name;
    std::stringstream ss(name);
    ss << timeline.value->name() << " Flattened";
    auto newtimeline = otio::SerializableObject::Retainer<otio::Timeline>(new otio::Timeline(ss.str()));
    auto stack = otio::SerializableObject::Retainer<otio::Stack>(new otio::Stack());
    if (!stack.value->append_child(onetrack, &error_status))
    {
        print_error(error_status);
        return 1;            
    }

    // keep the audio track(s) as-is
    // TODO: What is the C++ equivalent of deepcopy?
    //newtimeline.tracks.extend(copy.deepcopy(audio_tracks))
    
    newtimeline.value->set_tracks(stack);

    // ...and save it to disk.
    std::cout << "Saving " << newtimeline.value->video_tracks().size() << " video tracks and " <<
        newtimeline.value->audio_tracks().size() << " audio tracks." << std::endl;
    if (!timeline.value->to_json_file(argv[2], &error_status))
    {
        print_error(error_status);
        return 1;            
    }

    return 0;
}
