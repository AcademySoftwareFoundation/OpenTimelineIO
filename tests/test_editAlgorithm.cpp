// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/mediaReference.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/algo/editAlgorithm.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/track.h>
#include <opentimelineio/transition.h>

// Uncomment this for debugging output
<<<<<<< HEAD
//#define DEBUG
=======
// #define DEBUG
>>>>>>> test_edit_commands


namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

using otime::RationalTime;
using otime::TimeRange;
using otio::algo::ReferencePoint;

#ifdef DEBUG

#include <iostream>


std::ostream& operator << (std::ostream& os, const RationalTime& value)
{
    os << std::fixed << value.value() << "/" << value.rate();
    return os;
}

std::ostream& operator << (std::ostream& os, const TimeRange& value)
{
    os << std::fixed << value.start_time().value() << "/" <<
        value.duration().value() << "/" <<
        value.duration().rate();
    return os;
}

#endif

namespace {

void
debug_track_ranges(const std::string& title, otio::Track* track)
{
#ifdef DEBUG
    std::cout << "\t" << title << " TRACK RANGES" << std::endl;
<<<<<<< HEAD
=======
    double rate = 0;
>>>>>>> test_edit_commands
    for (const auto& child: track->children())
    {
        auto item = otio::dynamic_retainer_cast<otio::Item>(child);
        if (item)
<<<<<<< HEAD
            std::cout << "\t\t" << item->name() << " "
                      << track->trimmed_range_of_child(child).value()
                      << std::endl;
        auto transition = otio::dynamic_retainer_cast<otio::Transition>(child);
        if (transition)
            std::cout << "\t\t" << transition->name() << " "
                      << track->trimmed_range_of_child(transition).value()
                      << std::endl;
=======
        {
            auto range = track->trimmed_range_of_child(child).value();
            std::cout << "\t\t" << item->name() << " " << range
                      << " start=" << range.start_time().to_seconds()
                      << " end=" << range.end_time_exclusive().to_seconds()
                      << " duration=" << range.duration().to_seconds()
                      << std::endl;
            if (range.duration().rate() > rate) rate = range.duration().rate();
        }
        auto transition = otio::dynamic_retainer_cast<otio::Transition>(child);
        if (transition)
        {
            auto range = track->trimmed_range_of_child(child).value();
            std::cout << "\t\t" << transition->name() << " " << range
                      << std::endl;
        }
>>>>>>> test_edit_commands
    }
    std::cout << "\t" << title << " TRACK RANGES END" << std::endl;
#endif
}

void
debug_clip_ranges(const std::string& title, otio::Track* track)
{
#ifdef DEBUG
    std::cout << "\t" << title << " CLIP TRIMMED RANGES" << std::endl;
    for (const auto& child: track->children())
    {
        auto item = otio::dynamic_retainer_cast<otio::Item>(child);
        if (item)
<<<<<<< HEAD
            std::cout << "\t\t" << item->name() << " " << item->trimmed_range()
                      << std::endl;
=======
        {
            auto range = item->trimmed_range();
            std::cout << "\t\t" << item->name() << " " << range
                      << " seconds=" << range.start_time().to_seconds()
                      << " - " << range.duration().to_seconds()
                      << std::endl;
        }
>>>>>>> test_edit_commands
    }
    std::cout << "\t" << title << " CLIP TRIMMED RANGES END" << std::endl;
#endif
}

void
assert_clip_ranges(
    otio::Track*                  track,
    const std::vector<TimeRange>& expected_ranges)
{
    std::vector<otio::TimeRange> ranges;
    size_t children = 0;
    for (const auto& child: track->children())
    {
        auto item = otio::dynamic_retainer_cast<otio::Item>(child);
        if (item)
        {
            ranges.push_back(item->trimmed_range());
            ++children;
        }
    }
    debug_clip_ranges("TEST", track);
    assertEqual(children, expected_ranges.size());
    assertEqual(expected_ranges, ranges);
}

void
assert_track_ranges(
    otio::Track*                  track,
    const std::vector<TimeRange>& expected_ranges)
{
    std::vector<otio::TimeRange> ranges;
    size_t children = 0;
    for (const auto& child: track->children())
    {
        auto item = otio::dynamic_retainer_cast<otio::Item>(child);
        if (item)
        {
            ranges.push_back(track->trimmed_range_of_child(child).value());
            ++children;
        }
    }
    debug_track_ranges("TEST", track);
    assertEqual(children, ranges.size());
    assertEqual(expected_ranges, ranges);
}

void
test_edit_slice(
    const TimeRange&              clip_range,
    const RationalTime&           slice_time,
    const std::vector<TimeRange>& slice_ranges)
{
    // Create a track with one clip.
    otio::SerializableObject::Retainer<otio::Clip> clip_0 =
        new otio::Clip("clip_0", nullptr, clip_range);
    otio::SerializableObject::Retainer<otio::Track> track = new otio::Track();
    track->append_child(clip_0); 

    debug_track_ranges("START", track);
#ifdef DEBUG
    std::cout << "\t\tslice at " << slice_time << std::endl;
#endif
    
    // Slice.
    otio::algo::slice(track, slice_time);

    // Asserts.
    assert_track_ranges(track, slice_ranges);
}


void
test_edit_slice_transitions(
    const RationalTime&           slice_time,
    const std::vector<TimeRange>& slice_ranges)
{
    // Create a track with two clips and one transition.
    otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
        "clip_0",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
        "clip_1",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
        "clip_2",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_3 = new otio::Clip(
<<<<<<< HEAD
        "clip_2",
=======
        "clip_3",
>>>>>>> test_edit_commands
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(25.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Transition> transition_0 =
        new otio::Transition(
            "transition_0",
            otio::Transition::Type::SMPTE_Dissolve,
            RationalTime(5.0, 24.0),
            RationalTime(3.0, 24.0));
    otio::SerializableObject::Retainer<otio::Transition> transition_1 =
        new otio::Transition(
            "transition_1",
            otio::Transition::Type::SMPTE_Dissolve,
            RationalTime(5.0, 24.0),
            RationalTime(3.0, 24.0));
    otio::SerializableObject::Retainer<otio::Track> track = new otio::Track();
    track->append_child(clip_0); 
    track->append_child(clip_1);
    track->insert_child(1, transition_0);
    track->append_child(clip_2);
    track->append_child(clip_3);
    track->append_child(transition_1);

    debug_track_ranges("START", track);
#ifdef DEBUG
    std::cout << "\t\tslice transitions at " << slice_time << std::endl;
#endif
    
    // Slice.
    otio::algo::slice(track, slice_time);

    // Asserts.
    assert_track_ranges(track, slice_ranges);
}

void
test_edit_slip(
    const TimeRange&              media_range,
    const TimeRange&              clip_range,
    const RationalTime&           slip_time,
    const TimeRange slip_range)
{
    // Create one clip with one media.
    otio::SerializableObject::Retainer<otio::MediaReference>
        media_0 = new otio::MediaReference(
            "media_0",
            media_range);
    otio::SerializableObject::Retainer<otio::Clip> clip_0 =
        new otio::Clip("clip_0", media_0, clip_range);
    
    // Slip.
    otio::algo::slip(clip_0, slip_time);

    // Asserts.
    const otio::TimeRange& range = clip_0->trimmed_range();
    assertEqual(slip_range, range);
}

    
void
test_edit_slide(
    const TimeRange&              media_range,
    const RationalTime&           slide_time,
    const std::vector<TimeRange>& slide_ranges)
{
    // Create a track with three clips.
    otio::SerializableObject::Retainer<otio::MediaReference>
        media_0 = new otio::MediaReference(
            "media_0",
            media_range);
    otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
        "clip_0",
        media_0,
        otio::TimeRange(
            otio::RationalTime(0.0, 24.0),
            otio::RationalTime(24.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
        "clip_1",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(0.0, 24.0),
            otio::RationalTime(30.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
        "clip_2",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(0.0, 24.0),
            otio::RationalTime(40.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Track> track =
        new otio::Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    // Slide.
    otio::algo::slide(clip_1, slide_time);

    // Asserts.
    assert_track_ranges(track, slide_ranges);
}

void test_edit_ripple(
    const RationalTime&           delta_in,
    const RationalTime&           delta_out,
    const std::vector<TimeRange>& track_ranges,
    const std::vector<TimeRange>& item_ranges
    )
{
    // Create a track with one gap and two clips.
    otio::SerializableObject::Retainer<otio::Gap> clip_0 = new otio::Gap(
        otio::TimeRange(
            otio::RationalTime(0.0, 24.0),
            otio::RationalTime(20.0, 24.0)),
        "gap_0");
    otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
        "clip_1",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(5.0, 24.0),
            otio::RationalTime(25.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
        "clip_2",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(5.0, 24.0),
            otio::RationalTime(20.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Track> track = new otio::Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    debug_track_ranges("START", track);
    debug_clip_ranges("START", track);

#ifdef DEBUG
    std::cout << "RIPPLE  DELTA_IN=" << delta_in << std::endl;
    std::cout << "RIPPLE DELTA_OUT=" << delta_out << std::endl;
#endif
    otio::ErrorStatus error_status;
    otio::algo::ripple(
        clip_1,
        delta_in,
        delta_out,
        &error_status);

    // Asserts.
    assert(!otio::is_error(error_status));
    assert_track_ranges(track, track_ranges);
    assert_clip_ranges(track, item_ranges);
}

void test_edit_roll(
    const RationalTime&           delta_in,
    const RationalTime&           delta_out,
    const std::vector<TimeRange>& track_ranges,
    const std::vector<TimeRange>& item_ranges
    )
{
    // Create a track with one gap and two clips.
    otio::SerializableObject::Retainer<otio::Gap> clip_0 = new otio::Gap(
        otio::TimeRange(
            otio::RationalTime(0.0, 24.0),
            otio::RationalTime(20.0, 24.0)),
        "gap_0");
    otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
        "clip_1",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(5.0, 24.0),
            otio::RationalTime(30.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
        "clip_2",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(5.0, 24.0),
            otio::RationalTime(20.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Track> track = new otio::Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    debug_track_ranges("START", track);
    debug_clip_ranges("START", track);

#ifdef DEBUG
    std::cout << "ROLL  DELTA_IN=" << delta_in << std::endl;
    std::cout << "ROLL DELTA_OUT=" << delta_out << std::endl;
#endif
    otio::ErrorStatus error_status;
    otio::algo::roll(
        clip_1,
        delta_in,
        delta_out,
        &error_status);

    // Asserts.
    assert(!otio::is_error(error_status));
    assert_track_ranges(track, track_ranges);
    assert_clip_ranges(track, item_ranges);
}

void test_edit_fill(
    const TimeRange&              clip_range,
    const RationalTime&           track_time,
    const ReferencePoint&         reference_point,
    const std::vector<TimeRange>& track_ranges,
    const std::vector<TimeRange>& item_ranges
    )
{
    // Create a track with one gap and two clips.  We leave one clip for fill.
    otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
        "clip_0",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(0.0, 24.0),
            otio::RationalTime(20.0, 24.0)));
    otio::SerializableObject::Retainer<otio::Gap> clip_1 = new otio::Gap(
        otio::TimeRange(
            otio::RationalTime(5.0, 24.0),
            otio::RationalTime(30.0, 24.0)),
        "gap_0");
    otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
        "clip_2",
        nullptr,
        otio::TimeRange(
            otio::RationalTime(5.0, 24.0),
            otio::RationalTime(20.0, 24.0)));
    
    otio::SerializableObject::Retainer<otio::Clip> clip_3 = new otio::Clip(
        "fill_1",
        nullptr,
        clip_range);

    otio::SerializableObject::Retainer<otio::Track> track = new otio::Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    auto duration = track->duration();
    
    debug_clip_ranges("START", track);
    debug_track_ranges("START", track);

    otio::ErrorStatus error_status;
    otio::algo::fill(
        clip_3,
        track,
        track_time,
        reference_point,
        &error_status);

    auto new_duration = track->duration();
    
    // Asserts.
    if (reference_point == ReferencePoint::Sequence)
    {
#ifdef DEBUG
        std::cout << "new duration=" << new_duration << " old=" << duration << std::endl;
#endif
        assertEqual(new_duration, duration);
    }
    assert(!otio::is_error(error_status));
<<<<<<< HEAD
    assert_clip_ranges(track, item_ranges);
    assert_track_ranges(track, track_ranges);
=======
    assert_track_ranges(track, track_ranges);
    assert_clip_ranges(track, item_ranges);
>>>>>>> test_edit_commands
}

} // namespace

int
main(int argc, char** argv)
{
    Tests tests;
    
<<<<<<< HEAD
    tests.add_test("test_edit_slice", [] {
=======
    tests.add_test("test_edit_slice_1", [] {
>>>>>>> test_edit_commands
        // Slice in the middle.
        test_edit_slice(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
            RationalTime(12.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(12.0, 24.0), RationalTime(12.0, 24.0)) });

        // Slice at the beginning.
        test_edit_slice(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
            RationalTime(0.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)) });

        // Slice near the beginning.
        test_edit_slice(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
            RationalTime(1.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(1.0, 24.0), RationalTime(23.0, 24.0)) });

        // Slice near the end.
        test_edit_slice(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
            RationalTime(23.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(23.0, 24.0)),
              TimeRange(RationalTime(23.0, 24.0), RationalTime(1.0, 24.0)) });

        // Slice at the end.
        test_edit_slice(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
            RationalTime(24.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)) });
        
    });

<<<<<<< HEAD
=======
    tests.add_test("test_edit_slice_2", [] {
        // Create a track with three clips of different rates
        // Slice the clips several times at different points.
        // Delete an item and slice again at same point.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 23.98),
                otio::RationalTime(71.94, 23.98)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 23.98),
                otio::RationalTime(71.94, 23.98)));
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_2",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(90.0, 30.0),
                otio::RationalTime(90.0, 30.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);
        
        // Slice.
        otio::ErrorStatus error_status;
        otio::algo::slice(
            track,
            RationalTime(121.0, 30.0),
            true,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(31.0, 30.0),
                                    RationalTime(59, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(121.0, 30.0),
                                    RationalTime(59, 30.0)),
                                TimeRange(
                                    RationalTime(180.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });

        otio::algo::slice(
            track,
            RationalTime(122.0, 30.0),
            true,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(31.0, 30.0),
                                    RationalTime(1, 30.0)),
                                TimeRange(
                                    RationalTime(32.0, 30.0),
                                    RationalTime(58, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(121.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(122.0, 30.0),
                                    RationalTime(58, 30.0)),
                                TimeRange(
                                    RationalTime(180.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });

        track->remove_child(2); // Delete the 1 frame item
        
        // Asserts.
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(32.0, 30.0),
                                    RationalTime(58, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(121.0, 30.0),
                                    RationalTime(58, 30.0)),
                                TimeRange(
                                    RationalTime(179.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });

        // Slice again at the same points (this slice does nothing at it is at
        // start point).
        otio::algo::slice(
            track,
            RationalTime(121.0, 30.0),
            true,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(32.0, 30.0),
                                    RationalTime(58, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(121.0, 30.0),
                                    RationalTime(58, 30.0)),
                                TimeRange(
                                    RationalTime(179.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });

        // Slice again for one frame
        otio::algo::slice(
            track,
            RationalTime(122.0, 30.0),
            true,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(32.0, 30.0),
                                    RationalTime(1, 30.0)),
                                TimeRange(
                                    RationalTime(33.0, 30.0),
                                    RationalTime(57, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(121.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(122.0, 30.0),
                                    RationalTime(57, 30.0)),
                                TimeRange(
                                    RationalTime(179.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        
        // Slice again for one frame
        otio::algo::slice(
            track,
            RationalTime(179.0, 30.0),
            true,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(32.0, 30.0),
                                    RationalTime(1, 30.0)),
                                TimeRange(
                                    RationalTime(33.0, 30.0),
                                    RationalTime(57, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(31.0, 30.0)),
                                TimeRange(
                                    RationalTime(121.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(122.0, 30.0),
                                    RationalTime(57, 30.0)),
                                TimeRange(
                                    RationalTime(179.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
    });

    
>>>>>>> test_edit_commands
    tests.add_test("test_edit_slice_transitions_1", [] {
        
        // Four clips with two transitions.
        test_edit_slice_transitions(
            RationalTime(24.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(74.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(104.0, 24.0), RationalTime(25.0, 24.0)) });
        
       test_edit_slice_transitions(
            RationalTime(23.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(23.0, 24.0)),
              TimeRange(RationalTime(23.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(74.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(104.0, 24.0), RationalTime(25.0, 24.0)) });
        
    });
    
    tests.add_test("test_edit_overwrite_0", [] {
        // Create a track with one clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);

        // Overwrite past the clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::ErrorStatus error_status;
        otio::algo::overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 3);
        assert(otio::dynamic_retainer_cast<otio::Gap>(track->children()[1]));
        const RationalTime duration = track->duration();
        assert(duration == otio::RationalTime(72.0, 24.0));
        auto range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(48.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
    });

    tests.add_test("test_edit_overwrite_1", [] {
        // Create a track with one clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
<<<<<<< HEAD
                otio::RationalTime(72.0, 24.0)));
=======
                otio::RationalTime(24.0, 24.0)));
>>>>>>> test_edit_commands
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);

<<<<<<< HEAD
        // Overwrite a portion inside the clip.
=======
        // Overwrite past the clip.
>>>>>>> test_edit_commands
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::ErrorStatus error_status;
        otio::algo::overwrite(
            clip_1,
            track,
<<<<<<< HEAD
            TimeRange(RationalTime(24.0, 24.0), RationalTime(24.0, 24.0)),
=======
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 3);
        assert(otio::dynamic_retainer_cast<otio::Gap>(track->children()[1]));
        const RationalTime duration = track->duration();
        assert(duration == otio::RationalTime(72.0, 24.0));
        auto range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(48.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
    });

    tests.add_test("test_edit_overwrite_2", [] {
        // Create a track with one clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(1.0, 24.0),
                otio::RationalTime(100.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);

        // Overwrite a single frame inside the clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(1.0, 24.0),
                otio::RationalTime(1.0, 24.0)));
        otio::ErrorStatus error_status;
        otio::algo::overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(42.0, 24.0), RationalTime(1.0, 24.0)),
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime duration = track->duration();
<<<<<<< HEAD
        assert(duration == otio::RationalTime(72.0, 24.0));
=======
        assert(duration == otio::RationalTime(100.0, 24.0));
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(1.0, 24.0),
                                    RationalTime(42.0, 24.0)),
                                TimeRange(
                                    RationalTime(1.0, 24.0),
                                    RationalTime(1.0, 24.0)),
                                TimeRange(
                                    RationalTime(44.0, 24.0),
                                    RationalTime(57.0, 24.0))
                            });
>>>>>>> test_edit_commands
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
<<<<<<< HEAD
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(24.0, 24.0),
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(48.0, 24.0),
                                    RationalTime(24.0, 24.0))
                            });
    });

    tests.add_test("test_edit_overwrite_2", [] {
        // Create a track with two clips.
=======
                                    RationalTime(42.0, 24.0)),
                                TimeRange(
                                    RationalTime(42.0, 24.0),
                                    RationalTime(1.0, 24.0)),
                                TimeRange(
                                    RationalTime(43.0, 24.0),
                                    RationalTime(57.0, 24.0))
                            });
    });

    tests.add_test("test_edit_overwrite_3", [] {
        // Create a track with two clips and overwrite a portion of both.
>>>>>>> test_edit_commands
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Overwrite both clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_2",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        const RationalTime duration = track->duration();
        otio::ErrorStatus  error_status;
        otio::algo::overwrite(
            clip_2,
            track,
            TimeRange(RationalTime(12.0, 24.0), RationalTime(24.0, 24.0)),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(duration, new_duration);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(12.0, 24.0),
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(36.0, 24.0),
                                    RationalTime(12.0, 24.0))
                            });
    });

    
<<<<<<< HEAD
=======
    tests.add_test("test_edit_overwrite_4", [] {
        // Create a track with one long clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(704.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);

        // Overwrite one portion of the clip.
        otio::SerializableObject::Retainer<otio::Clip> over_1 = new otio::Clip(
            "over_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(1.0, 24.0)));
        const RationalTime duration = track->duration();
        otio::ErrorStatus  error_status;
        otio::algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(272.0, 24.0), RationalTime(1.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(duration, new_duration);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(272.0, 24.0)),
                                TimeRange(
                                    RationalTime(272.0, 24.0),
                                    RationalTime(1.0, 24.0)),
                                TimeRange(
                                    RationalTime(273.0, 24.0),
                                    RationalTime(431.0, 24.0))
                            });
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(272.0, 24.0)),
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(1.0, 24.0)),
                                TimeRange(
                                    RationalTime(273.0, 24.0),
                                    RationalTime(431.0, 24.0))
                            });
    });

    tests.add_test("test_edit_overwrite_5", [] {
        // Create a track with one long clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(704.0, 30.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);

        // Overwrite one portion of the clip.
        otio::SerializableObject::Retainer<otio::Clip> over_1 = new otio::Clip(
            "over_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(1.0, 30.0)));
        const RationalTime duration = track->duration();
        otio::ErrorStatus  error_status;
        otio::algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(272.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(duration, new_duration);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(272.0, 30.0)),
                                TimeRange(
                                    RationalTime(272.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(273.0, 30.0),
                                    RationalTime(431.0, 30.0))
                            });
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(272.0, 30.0)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(273.0, 30.0),
                                    RationalTime(431.0, 30.0))
                            });

        // Overwrite another portion of the clip.
        otio::SerializableObject::Retainer<otio::Clip> over_2 = new otio::Clip(
            "over_2",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(1.0, 30.0)));
        
        otio::algo::overwrite(
            over_2,
            track,
            TimeRange(RationalTime(360.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);
        
        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration3 = track->duration();
        assertEqual(duration, new_duration3);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(272.0, 30.0)),
                                TimeRange(
                                    RationalTime(272.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(273.0, 30.0),
                                    RationalTime(87.0, 30.0)),
                                TimeRange(
                                    RationalTime(360.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(361.0, 30.0),
                                    RationalTime(343.0, 30.0))
                            });
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(272.0, 30.0)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(273.0, 30.0),
                                    RationalTime(87.0, 30.0)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(361.0, 30.0),
                                    RationalTime(343.0, 30.0))
                            });

        // Overwrite the same portion of the clip.
        otio::SerializableObject::Retainer<otio::Clip> over_3 = new otio::Clip(
            "over_3",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(1.0, 30.0)));
        
        otio::algo::overwrite(
            over_3,
            track,
            TimeRange(RationalTime(360.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);
        
        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration2 = track->duration();
        assertEqual(duration, new_duration2);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(272.0, 30.0)),
                                TimeRange(
                                    RationalTime(272.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(273.0, 30.0),
                                    RationalTime(87.0, 30.0)),
                                TimeRange(
                                    RationalTime(360.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(361.0, 30.0),
                                    RationalTime(343.0, 30.0))
                            });
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(272.0, 30.0)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(273.0, 30.0),
                                    RationalTime(87.0, 30.0)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(361.0, 30.0),
                                    RationalTime(343.0, 30.0))
                            });
    });

    tests.add_test("test_edit_overwrite_6", [] {
        // Create a track with three clips of different rates.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 23.98),
                otio::RationalTime(71.94, 23.98)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 23.98),
                otio::RationalTime(71.94, 23.98)));
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_2",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(90.0, 30),
                otio::RationalTime(90.0, 30)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);

        // Overwrite one portion of the clip.
        otio::SerializableObject::Retainer<otio::Clip> over_1 = new otio::Clip(
            "over_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 30.0),
                otio::RationalTime(1.0, 30.0)));

        debug_track_ranges("START", track);
        
        const RationalTime duration = track->duration();
        otio::ErrorStatus  error_status;
        otio::algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(137.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);

        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(duration, new_duration);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(90, 30.0),
                                    RationalTime(47.0, 30.0)),
                                TimeRange(
                                    RationalTime(137.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(138.0, 30.0),
                                    RationalTime(42.0, 30.0)),
                                TimeRange(
                                    RationalTime(180.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
        assert_clip_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 23.98),
                                    RationalTime(71.94, 23.98)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(47.0, 30.0)),
                                TimeRange(
                                    RationalTime(0.0, 30.0),
                                    RationalTime(1.0, 30.0)),
                                TimeRange(
                                    RationalTime(48.0, 30.0),
                                    RationalTime(42.0, 30.0)),
                                TimeRange(
                                    RationalTime(90.0, 30.0),
                                    RationalTime(90.0, 30.0))
                            });
    });

    
>>>>>>> test_edit_commands
    // Insert at middle of clip_0
    tests.add_test("test_edit_insert_1", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(12.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 4);
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(12.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(24.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(36.0, 24.0),
                                    RationalTime(24.0, 24.0))
                            });
    });

    // Insert at start of clip_0.
    tests.add_test("test_edit_insert_2", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(0.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 3);
        
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(12.0, 24.0),
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(36.0, 24.0),
                                    RationalTime(24.0, 24.0))
                            });
    });
    
    // Insert at start of clip_1 (insert at 0 index).
    tests.add_test("test_edit_insert_3", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(-1.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 3);
        
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        auto range = clip_0->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(12.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(36.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        range = insert_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
    });
    
    // Insert at start of clip_1.
    tests.add_test("test_edit_insert_4", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(24.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(24.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(36.0, 24.0),
                                    RationalTime(24.0, 24.0))
                            });
    });
    
    // Insert at end of clip_1 (append at end).
    tests.add_test("test_edit_insert_4", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(48.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(24.0, 24.0),
                                    RationalTime(24.0, 24.0)),
                                TimeRange(
                                    RationalTime(48.0, 24.0),
                                    RationalTime(12.0, 24.0))
                            });
    });
    
    // Insert near the beginning of clip_0.
    tests.add_test("test_edit_insert_5", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(1.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(1.0, 24.0)),
                                TimeRange(
                                    RationalTime(1.0, 24.0),
                                    RationalTime(12.0, 24.0)),
                                TimeRange(
                                    RationalTime(13.0, 24.0),
                                    RationalTime(23.0, 24.0)),
                                TimeRange(
                                    RationalTime(36.0, 24.0),
                                    RationalTime(24.0, 24.0))
                            });
    });
    
    // Insert near the end of clip_1.
    tests.add_test("test_edit_insert_6", [] {
        // Create a track with two clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_0 = new otio::Clip(
            "clip_0",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        otio::SerializableObject::Retainer<otio::Clip> insert_1 = new otio::Clip(
            "insert_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        otio::ErrorStatus  error_status;
        otio::algo::insert(
            insert_1,
            track,
            RationalTime(47.0, 24.0),
<<<<<<< HEAD
=======
            true,
>>>>>>> test_edit_commands
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        assert_track_ranges(track,
                            {
                                otio::TimeRange(
                                    otio::RationalTime(0.0, 24.0),
                                    otio::RationalTime(24.0, 24.0)),
                                otio::TimeRange(
                                    otio::RationalTime(24.0, 24.0),
                                    otio::RationalTime(23.0, 24.0)),
                                otio::TimeRange(
                                    otio::RationalTime(47.0, 24.0),
                                    otio::RationalTime(12.0, 24.0)),
                                otio::TimeRange(
                                    otio::RationalTime(59.0, 24.0),
                                    otio::RationalTime(1.0, 24.0)),
                            });
    });
    
    tests.add_test("test_edit_slip", [] {
        const TimeRange media_range(
            RationalTime(-15.0, 24.0),
            RationalTime(63.0, 24.0));
        const TimeRange clip_range(
            RationalTime(0.0, 24.0),
            RationalTime(36.0, 24.0));

        // Slip +5 frames.
        test_edit_slip(
            media_range,
            clip_range,
            RationalTime(5.0, 24.0),
            TimeRange(RationalTime(5.0, 24.0), RationalTime(36.0, 24.0)));
        
        // Slip +12 frames.
        test_edit_slip(
            media_range,
            clip_range,
            RationalTime(12.0, 24.0),
            TimeRange(RationalTime(12.0, 24.0), RationalTime(36.0, 24.0)));
        
        // Slip +20 frames.
        test_edit_slip(
            media_range,
            clip_range,
            RationalTime(20.0, 24.0),
            TimeRange(RationalTime(12.0, 24.0), RationalTime(36.0, 24.0)));

        // Slip -5 frames
        test_edit_slip(
            media_range,
            clip_range,
            RationalTime(-5.0, 24.0),
            TimeRange(RationalTime(-5.0, 24.0), RationalTime(36.0, 24.0)));
        
        // Slip -15 frames
        test_edit_slip(
            media_range,
            clip_range,
            RationalTime(-15.0, 24.0),
            TimeRange(RationalTime(-15.0, 24.0), RationalTime(36.0, 24.0)));
        
        // Slip -30 frames
        test_edit_slip(
            media_range,
            clip_range,
            RationalTime(-30.0, 24.0),
            TimeRange(RationalTime(-15.0, 24.0), RationalTime(36.0, 24.0)));
    });
        
    tests.add_test("test_edit_slide", [] {
        TimeRange media_range(
            RationalTime(0.0, 24.0),
            RationalTime(48.0, 24.0));
        
        // Slide 0.  No change.
        test_edit_slide(
            media_range,
            RationalTime(0.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(54.0, 24.0), RationalTime(40.0, 24.0)) });
        
        // Slide right +12.
        test_edit_slide(
            media_range,
            RationalTime(12.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(36.0, 24.0)),
              TimeRange(RationalTime(36.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(66.0, 24.0), RationalTime(40.0, 24.0)) });
        
        // Slide right +48, which will clamp.
        test_edit_slide(
            media_range,
            RationalTime(48.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(48.0, 24.0)),
              TimeRange(RationalTime(48.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(78.0, 24.0), RationalTime(40.0, 24.0)) });
        
        // Slide left -10.
        test_edit_slide(
            media_range,
            RationalTime(-10.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(14.0, 24.0)),
              TimeRange(RationalTime(14.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(44.0, 24.0), RationalTime(40.0, 24.0)) });
        
        // Slide left -24, which is invalid.  No change.
        test_edit_slide(
            media_range,
            RationalTime(-24.0, 24.0),
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(54.0, 24.0), RationalTime(40.0, 24.0)) });
        
    });

    tests.add_test("test_edit_trim_1", [] {
        
        // Create a track with one gap and two clips.
        otio::SerializableObject::Retainer<otio::Gap> clip_0 = new otio::Gap(
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(20.0, 24.0)),
            "gap_0");
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(5.0, 24.0),
                otio::RationalTime(50.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(10.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);
        const RationalTime duration = track->duration();

        otio::ErrorStatus  error_status;
        otio::algo::trim(
            clip_1,
            RationalTime(5.0, 24.0),
            RationalTime(0.0, 24.0),
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(new_duration, duration);
        assert_track_ranges(track,
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(25.0, 24.0)),
                                TimeRange(
                                    RationalTime(25.0, 24.0),
                                    RationalTime(45.0, 24.0)),
                                TimeRange(
                                    RationalTime(70.0, 24.0),
                                    RationalTime(10.0, 24.0))
                            });
    });
    
    // Test trim delta_out right (no change due to clip).
    tests.add_test("test_edit_trim_2", [] {
        // Create a track with one gap and two clips.
        otio::SerializableObject::Retainer<otio::Gap> clip_0 = new otio::Gap(
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(20.0, 24.0)),
            "gap_0");
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(5.0, 24.0),
                otio::RationalTime(50.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(10.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);
        
        const RationalTime duration = track->duration();

        otio::ErrorStatus  error_status;
        otio::algo::trim(
            clip_1,
            RationalTime(0.0, 24.0),
            RationalTime(5.0, 24.0),
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(new_duration, duration);
        assert_track_ranges(track,
                          {
                              TimeRange(
                                  RationalTime(0.0, 24.0),
                                  RationalTime(20.0, 24.0)),
                              TimeRange(
                                  RationalTime(20.0, 24.0),
                                  RationalTime(50.0, 24.0)),
                              TimeRange(
                                  RationalTime(70.0, 24.0),
                                  RationalTime(10.0, 24.0))
                          });
        assert_clip_ranges(track,
<<<<<<< HEAD
                            {
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(20.0, 24.0)),
                                TimeRange(
                                    RationalTime(5.0, 24.0),
                                    RationalTime(50.0, 24.0)),
                                TimeRange(
                                    RationalTime(0.0, 24.0),
                                    RationalTime(10.0, 24.0))
                            });
=======
                           {
                               TimeRange(
                                   RationalTime(0.0, 24.0),
                                   RationalTime(20.0, 24.0)),
                               TimeRange(
                                   RationalTime(5.0, 24.0),
                                   RationalTime(50.0, 24.0)),
                               TimeRange(
                                   RationalTime(0.0, 24.0),
                                   RationalTime(10.0, 24.0))
                           });
>>>>>>> test_edit_commands
    });
        
    // Test trim delta_out left (create a gap)
    tests.add_test("test_edit_trim_3", [] {
        // Create a track with one gap and two clips.
        otio::SerializableObject::Retainer<otio::Gap> clip_0 = new otio::Gap(
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(20.0, 24.0)),
            "gap_0");
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(5.0, 24.0),
                otio::RationalTime(50.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(10.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);
        
        const RationalTime duration = track->duration();

        otio::ErrorStatus  error_status;
        otio::algo::trim(
            clip_1,
            RationalTime(0.0, 24.0),
            RationalTime(-5.0, 24.0),
            nullptr,
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(new_duration, duration);
        assert_track_ranges(track,
                          {
                              TimeRange(
                                  RationalTime(0.0, 24.0),
                                  RationalTime(20.0, 24.0)),
                              TimeRange(
                                  RationalTime(20.0, 24.0),
                                  RationalTime(45.0, 24.0)),
                              TimeRange(
                                  RationalTime(65.0, 24.0),
                                  RationalTime(5.0, 24.0)),
                              TimeRange(
                                  RationalTime(70.0, 24.0),
                                  RationalTime(10.0, 24.0))
                          });
        assert_clip_ranges(track,
                          {
                              TimeRange(
                                  RationalTime(0.0, 24.0),
                                  RationalTime(20.0, 24.0)),
                              TimeRange(
                                  RationalTime(5.0, 24.0),
                                  RationalTime(45.0, 24.0)),
                              TimeRange(
                                  RationalTime(0.0, 24.0),
                                  RationalTime(5.0, 24.0)),
                              TimeRange(
                                  RationalTime(0.0, 24.0),
                                  RationalTime(10.0, 24.0))
                          });
    });
    
    // Test ripple
    tests.add_test("test_edit_ripple_1", [] {
        test_edit_ripple(
            RationalTime(10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(35.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(15.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            });
    });
    
    tests.add_test("test_edit_ripple_2", [] {
        test_edit_ripple(
            RationalTime(-10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            });
    });

    
    tests.add_test("test_edit_ripple_3", [] {
        test_edit_ripple(
            RationalTime(0.0, 24.0),
            RationalTime(10.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(55.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    
    tests.add_test("test_edit_ripple_4", [] {
        test_edit_ripple(
            RationalTime(0.0, 24.0),
            RationalTime(-10.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(35.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });
    
    tests.add_test("test_edit_roll_1", [] {
        test_edit_roll(
            RationalTime(10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(30.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(15.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    tests.add_test("test_edit_roll_2", [] {
        test_edit_roll(
            RationalTime(-10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(15.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    tests.add_test("test_edit_roll_3", [] {
        test_edit_roll(
            RationalTime(0.0, 24.0),
            RationalTime(10.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(40.0, 24.0)),
                TimeRange(
                    RationalTime(60.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(40.0, 24.0)),
                TimeRange(
                    RationalTime(15.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    tests.add_test("test_edit_roll_4", [] {
        test_edit_roll(
            RationalTime(0.0, 24.0),
            RationalTime(-10.0, 24.0),
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(25.0, 24.0)),
                TimeRange(
                    RationalTime(45.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(25.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    // Add longer clip in gap as Fit reference point
    // (creates linearTimeWarp effect).
    tests.add_test("test_edit_fill_1", [] {
        test_edit_fill(
            TimeRange(
                RationalTime(0.0, 24.0),
                RationalTime(35.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Fit, 
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(55.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    // Add longer clip at gap as Source reference point.
    // Stretches timeline.
    tests.add_test("test_edit_fill_2", [] {
        test_edit_fill(
            TimeRange(
                RationalTime(0.0, 24.0),
                RationalTime(35.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Source,
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(55.0, 24.0),
                    RationalTime(5.0, 24.0)),
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(35.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(5.0, 24.0)),
            }); 
    });


    // Add equal clip in gap as Source reference point
    tests.add_test("test_edit_fill_3", [] {
        test_edit_fill(
            TimeRange(
                RationalTime(0.0, 24.0),
                RationalTime(30.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Source,
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    // Add shorter clip in gap as Source reference point
    tests.add_test("test_edit_fill_4", [] {
        test_edit_fill(
            TimeRange(
                RationalTime(0.0, 24.0),
                RationalTime(5.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Source,
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(5.0, 24.0)),
                TimeRange(
                    RationalTime(25.0, 24.0),
                    RationalTime(25.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(5.0, 24.0)),
                TimeRange(
<<<<<<< HEAD
                    RationalTime(5.0, 24.0),
=======
                    RationalTime(10.0, 24.0),
>>>>>>> test_edit_commands
                    RationalTime(25.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });

    // Add an equal clip (after trim) in gap as
    // Sequence reference point.
    tests.add_test("test_edit_fill_5", [] {

        test_edit_fill(
            TimeRange(
                RationalTime(0.0, 24.0),
                RationalTime(35.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(30.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });
    
    // Add a longer clip in gap as Sequence reference point
    tests.add_test("test_edit_fill_6", [] {

        test_edit_fill(
            TimeRange(
                RationalTime(-10.0, 24.0),
                RationalTime(30.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(35.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(15.0, 24.0)),
                TimeRange(
<<<<<<< HEAD
                    RationalTime(5.0, 24.0),
=======
                    RationalTime(20.0, 24.0),
>>>>>>> test_edit_commands
                    RationalTime(15.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });


    // Add a shorter clip in gap as Sequence reference point
    tests.add_test("test_edit_fill_7", [] {

        test_edit_fill(
            TimeRange(
                RationalTime(10.0, 24.0),
                RationalTime(5.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(20.0, 24.0),
                    RationalTime(5.0, 24.0)),
                TimeRange(
                    RationalTime(25.0, 24.0),
                    RationalTime(25.0, 24.0)),
                TimeRange(
                    RationalTime(50.0, 24.0),
                    RationalTime(20.0, 24.0))
            },
            // Clip Ranges
            {
                TimeRange(
                    RationalTime(0.0, 24.0),
                    RationalTime(20.0, 24.0)),
                TimeRange(
                    RationalTime(10.0, 24.0),
                    RationalTime(5.0, 24.0)),
                TimeRange(
<<<<<<< HEAD
                    RationalTime(5.0, 24.0),
=======
                    RationalTime(10.0, 24.0),
>>>>>>> test_edit_commands
                    RationalTime(25.0, 24.0)),
                TimeRange(
                    RationalTime(5.0, 24.0),
                    RationalTime(20.0, 24.0))
            }); 
    });
    
    
    tests.run(argc, argv);
    return 0;
}
