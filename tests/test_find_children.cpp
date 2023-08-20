// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/mediaReference.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/algo/editAlgorithm.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>
#include <opentimelineio/transition.h>

// Uncomment this for debugging output
// #define DEBUG

int
main(int argc, char** argv)
{
    Tests tests;
    
    // Find children works with one track
    tests.add_test("test_find_children_ok", [] {
        // Create a timeline, stack and two tracks with one clip each.
        otio::SerializableObject::Retainer<otio::Clip> video_clip = new otio::Clip(
            "video_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(704.0, 30.0)));
        otio::SerializableObject::Retainer<otio::Track> video_track = new otio::Track("Video");
        otio::SerializableObject::Retainer<otio::Stack> stack = new otio::Stack();
        otio::SerializableObject::Retainer<otio::Timeline> timeline = new otio::Timeline();
        video_track->append_child(video_clip);

        stack->append_child(video_track);

        timeline->set_tracks(stack);

        RationalTime time(704.0, 30.0);
        RationalTime one_frame(1.0, 30.0);
        TimeRange range(time, one_frame);
        otio::ErrorStatus errorStatus;
        auto items = timeline->find_children(&errorStatus, range);
        assert(!otio::is_error(errorStatus));
        assert(!items.empty());
    });
    
    // Find children seems broken with two tracks
    tests.add_test("test_find_children_broken", [] {
        
        // Create a timeline, stack and two tracks with one clip each.
        otio::SerializableObject::Retainer<otio::Clip> video_clip = new otio::Clip(
            "video_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(704.0, 30.0)));
        otio::SerializableObject::Retainer<otio::Clip> audio_clip = new otio::Clip(
            "audio_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(5.0, 24.0),
                otio::RationalTime(20.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> video_track = new otio::Track("Video");
        otio::SerializableObject::Retainer<otio::Track> audio_track = new otio::Track("Audio");
        otio::SerializableObject::Retainer<otio::Stack> stack = new otio::Stack();
        otio::SerializableObject::Retainer<otio::Timeline> timeline = new otio::Timeline();
        video_track->append_child(video_clip);
        audio_track->append_child(audio_clip);

        stack->append_child(video_track);
        stack->append_child(audio_track);

        timeline->set_tracks(stack);

        RationalTime time(704.0, 30.0);
        RationalTime one_frame(1.0, 30.0);
        TimeRange range(time, one_frame);
        otio::ErrorStatus errorStatus;
        auto items = timeline->find_children(&errorStatus, range);
        assert(!otio::is_error(errorStatus));
        assert(!items.empty());
    });
    
    tests.run(argc, argv);
    return 0;
}
