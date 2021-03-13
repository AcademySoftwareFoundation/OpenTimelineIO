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
    PythonAdapters adapters;
    otio::ErrorStatus error_status;
    auto timeline = adapters.read_from_file(argv[1], &error_status);
    if (!timeline)
    {
        print_error(error_status);
        return 1;
    }
    auto video_tracks = timeline->video_tracks();
    auto audio_tracks = timeline->audio_tracks();
    
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
    ss << timeline->name() << " Flattened";
    auto newtimeline = new otio::Timeline(ss.str());
    auto stack = new otio::Stack();
    if (!stack->append_child(onetrack, &error_status))
    {
        print_error(error_status);
        return 1;            
    }

    // keep the audio track(s) as-is
    // TODO: What is the C++ equivalent of deepcopy?
    //newtimeline.tracks.extend(copy.deepcopy(audio_tracks))
    
    newtimeline->set_tracks(stack);

    // ...and save it to disk.
    std::cout << "Saving " << newtimeline->video_tracks().size() << " video tracks and " <<
        newtimeline->audio_tracks().size() << " audio tracks." << std::endl;
    if (!adapters.write_to_file(newtimeline, argv[2], &error_status))
    {
        print_error(error_status);
        return 1;            
    }

    return 0;
}

