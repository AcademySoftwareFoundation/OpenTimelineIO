// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/algo/editAlgorithm.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/mediaReference.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>
#include <opentimelineio/transition.h>

// Uncomment this for debugging output
#define DEBUG

using namespace OTIO_NS;
using OTIO_NS::algo::ReferencePoint;

#ifdef DEBUG

#    include <iostream>

std::ostream&
operator<<(std::ostream& os, const RationalTime& value)
{
    os << std::fixed << value.value() << "/" << value.rate();
    return os;
}

std::ostream&
operator<<(std::ostream& os, const TimeRange& value)
{
    os << std::fixed << value.start_time().value() << "/"
       << value.duration().value() << "/" << value.duration().rate();
    return os;
}

#endif

namespace {

void
assert_duration(const RationalTime& new_duration, const RationalTime& duration)
{
#ifdef DEBUG
    std::cout << "\tnew duration=" << new_duration
              << " old duration=" << duration << std::endl;
#endif
    assertEqual(new_duration, duration);
}

void
debug_track_ranges(const std::string& title, Track* track)
{
#ifdef DEBUG
    std::cout << "\t" << title << " TRACK RANGES" << std::endl;
    for (const auto& child: track->children())
    {
        auto clip = dynamic_retainer_cast<Clip>(child);
        if (clip)
        {
            auto range = track->trimmed_range_of_child(child).value();
            std::cout << "\t\t" << clip->name() << " " << range << std::endl;
        }
        auto gap = dynamic_retainer_cast<Gap>(child);
        if (gap)
        {
            auto        range = track->trimmed_range_of_child(child).value();
            std::string name  = gap->name();
            if (name.empty())
                name = "gap";
            std::cout << "\t\t" << name << " " << range << std::endl;
        }
        auto transition = dynamic_retainer_cast<Transition>(child);
        if (transition)
        {
            auto        range = track->trimmed_range_of_child(child).value();
            std::string name  = transition->name();
            if (name.empty())
                name = "transition";
            std::cout << "\t\t" << name << " " << range << std::endl;
        }
    }
    std::cout << "\t" << title << " TRACK RANGES END" << std::endl;
#endif
}

void
debug_clip_ranges(const std::string& title, Track* track)
{
#ifdef DEBUG
    std::cout << "\t" << title << " CLIP TRIMMED RANGES" << std::endl;
    for (const auto& child: track->children())
    {
        auto clip = dynamic_retainer_cast<Clip>(child);
        if (clip)
        {
            auto range = clip->trimmed_range();
            std::cout << "\t\t" << clip->name() << " " << range << std::endl;
        }
        auto gap = dynamic_retainer_cast<Gap>(child);
        if (gap)
        {
            auto        range = gap->trimmed_range();
            std::string name  = gap->name();
            if (name.empty())
                name = "gap";
            std::cout << "\t\t" << name << " " << range << std::endl;
        }
    }
    std::cout << "\t" << title << " CLIP TRIMMED RANGES END" << std::endl;
#endif
}

void
assert_clip_ranges(Track* track, const std::vector<TimeRange>& expected_ranges)
{
    std::vector<TimeRange> ranges;
    size_t                 children = 0;
    for (const auto& child: track->children())
    {
        auto item = dynamic_retainer_cast<Item>(child);
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
assert_track_ranges(Track* track, const std::vector<TimeRange>& expected_ranges)
{
    std::vector<TimeRange> ranges;
    size_t                 children = 0;
    for (const auto& child: track->children())
    {
        auto item = dynamic_retainer_cast<Item>(child);
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
    SerializableObject::Retainer<Clip> clip_0 =
        new Clip("clip_0", nullptr, clip_range);
    SerializableObject::Retainer<Track> track = new Track();
    track->append_child(clip_0);

    debug_track_ranges("START", track);

    // Slice.
    algo::slice(track, slice_time);

    // Asserts.
    assert_track_ranges(track, slice_ranges);
}

void
test_edit_slice_transitions(
    const RationalTime&           slice_time,
    const std::vector<TimeRange>& slice_ranges)
{
    // Create a track with two clips and one transition.
    SerializableObject::Retainer<Clip> clip_0 = new Clip(
        "clip_0",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_1 = new Clip(
        "clip_1",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_2 = new Clip(
        "clip_2",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_3 = new Clip(
        "clip_3",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(25.0, 24.0)));
    SerializableObject::Retainer<Transition> transition_0 = new Transition(
        "transition_0",
        Transition::Type::SMPTE_Dissolve,
        RationalTime(5.0, 24.0),
        RationalTime(3.0, 24.0));
    SerializableObject::Retainer<Transition> transition_1 = new Transition(
        "transition_1",
        Transition::Type::SMPTE_Dissolve,
        RationalTime(5.0, 24.0),
        RationalTime(3.0, 24.0));
    SerializableObject::Retainer<Track> track = new Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->insert_child(1, transition_0);
    track->append_child(clip_2);
    track->append_child(clip_3);
    track->append_child(transition_1);

    debug_track_ranges("START", track);

    // Slice.
    algo::slice(track, slice_time);

    // Asserts.
    assert_track_ranges(track, slice_ranges);
}

void
test_edit_slip(
    const TimeRange&    media_range,
    const TimeRange&    clip_range,
    const RationalTime& slip_time,
    const TimeRange     slip_range)
{
    // Create one clip with one media.
    SerializableObject::Retainer<MediaReference> media_0 =
        new MediaReference("media_0", media_range);
    SerializableObject::Retainer<Clip> clip_0 =
        new Clip("clip_0", media_0, clip_range);

    // Slip.
    algo::slip(clip_0, slip_time);

    // Asserts.
    const TimeRange& range = clip_0->trimmed_range();
    assertEqual(slip_range, range);
}

void
test_edit_slide(
    const TimeRange&              media_range,
    const RationalTime&           slide_time,
    const std::vector<TimeRange>& slide_ranges)
{
    // Create a track with three clips.
    SerializableObject::Retainer<MediaReference> media_0 =
        new MediaReference("media_0", media_range);
    SerializableObject::Retainer<Clip> clip_0 = new Clip(
        "clip_0",
        media_0,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_1 = new Clip(
        "clip_1",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_2 = new Clip(
        "clip_2",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(40.0, 24.0)));
    SerializableObject::Retainer<Track> track = new Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    // Slide.
    algo::slide(clip_1, slide_time);

    // Asserts.
    assert_track_ranges(track, slide_ranges);
}

void
test_edit_ripple(
    const RationalTime&           delta_in,
    const RationalTime&           delta_out,
    const std::vector<TimeRange>& track_ranges,
    const std::vector<TimeRange>& item_ranges)
{
    // Create a track with one gap and two clips.
    SerializableObject::Retainer<Gap> clip_0 = new Gap(
        TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
        "gap_0");
    SerializableObject::Retainer<Clip> clip_1 = new Clip(
        "clip_1",
        nullptr,
        TimeRange(RationalTime(5.0, 24.0), RationalTime(25.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_2 = new Clip(
        "clip_2",
        nullptr,
        TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)));
    SerializableObject::Retainer<Track> track = new Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    OTIO_NS::ErrorStatus error_status;
    algo::ripple(clip_1, delta_in, delta_out, &error_status);

    // Asserts.
    assert(!is_error(error_status));
    assert_track_ranges(track, track_ranges);
    assert_clip_ranges(track, item_ranges);
}

void
test_edit_roll(
    const RationalTime&           delta_in,
    const RationalTime&           delta_out,
    const std::vector<TimeRange>& track_ranges,
    const std::vector<TimeRange>& item_ranges)
{
    // Create a track with one gap and two clips.
    SerializableObject::Retainer<Gap> clip_0 = new Gap(
        TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
        "gap_0");
    SerializableObject::Retainer<Clip> clip_1 = new Clip(
        "clip_1",
        nullptr,
        TimeRange(RationalTime(5.0, 24.0), RationalTime(30.0, 24.0)));
    SerializableObject::Retainer<Clip> clip_2 = new Clip(
        "clip_2",
        nullptr,
        TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)));
    SerializableObject::Retainer<Track> track = new Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    OTIO_NS::ErrorStatus error_status;
    algo::roll(clip_1, delta_in, delta_out, &error_status);

    // Asserts.
    assert(!is_error(error_status));
    assert_track_ranges(track, track_ranges);
    assert_clip_ranges(track, item_ranges);
}

void
test_edit_fill(
    const TimeRange&              clip_range,
    const RationalTime&           track_time,
    const ReferencePoint&         reference_point,
    const std::vector<TimeRange>& track_ranges,
    const std::vector<TimeRange>& item_ranges)
{
    // Create a track with one gap and two clips.  We leave one clip for fill.
    SerializableObject::Retainer<Clip> clip_0 = new Clip(
        "clip_0",
        nullptr,
        TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)));
    SerializableObject::Retainer<Gap> clip_1 = new Gap(
        TimeRange(RationalTime(5.0, 24.0), RationalTime(30.0, 24.0)),
        "gap_0");
    SerializableObject::Retainer<Clip> clip_2 = new Clip(
        "clip_2",
        nullptr,
        TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)));

    SerializableObject::Retainer<Clip> clip_3 =
        new Clip("fill_0", nullptr, clip_range);

    SerializableObject::Retainer<Track> track = new Track();
    track->append_child(clip_0);
    track->append_child(clip_1);
    track->append_child(clip_2);

    auto duration = track->duration();

    OTIO_NS::ErrorStatus error_status;
    algo::fill(clip_3, track, track_time, reference_point, &error_status);

    auto new_duration = track->duration();

    // Asserts.
    if (reference_point == ReferencePoint::Sequence)
    {
        assert_duration(new_duration, duration);
    }
    assert(!is_error(error_status));
    assert_track_ranges(track, track_ranges);
    assert_clip_ranges(track, item_ranges);
}

} // namespace

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_edit_slice_1", [] {
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

    tests.add_test("test_edit_slice_2", [] {
        // Create a track with three clips of different rates
        // Slice the clips several times at different points.
        // Delete an item and slice again at same point.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_2",
            nullptr,
            TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);

        // Slice.
        OTIO_NS::ErrorStatus error_status;
        algo::slice(track, RationalTime(121.0, 30.0), true, &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(31.0, 30.0), RationalTime(59, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(121.0, 30.0), RationalTime(59, 30.0)),
              TimeRange(RationalTime(180.0, 30.0), RationalTime(90.0, 30.0)) });

        algo::slice(track, RationalTime(122.0, 30.0), true, &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(31.0, 30.0), RationalTime(1, 30.0)),
              TimeRange(RationalTime(32.0, 30.0), RationalTime(58, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(121.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(122.0, 30.0), RationalTime(58, 30.0)),
              TimeRange(RationalTime(180.0, 30.0), RationalTime(90.0, 30.0)) });

        track->remove_child(2); // Delete the 1 frame item

        // Asserts.
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(32.0, 30.0), RationalTime(58, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });

        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(121.0, 30.0), RationalTime(58, 30.0)),
              TimeRange(RationalTime(179.0, 30.0), RationalTime(90.0, 30.0)) });

        // Slice again at the same points (this slice does nothing at it is at
        // start point).
        algo::slice(track, RationalTime(121.0, 30.0), true, &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(32.0, 30.0), RationalTime(58, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });

        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(121.0, 30.0), RationalTime(58, 30.0)),
              TimeRange(RationalTime(179.0, 30.0), RationalTime(90.0, 30.0)) });

        // Slice again for one frame
        algo::slice(track, RationalTime(122.0, 30.0), true, &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(32.0, 30.0), RationalTime(1, 30.0)),
              TimeRange(RationalTime(33.0, 30.0), RationalTime(57, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(121.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(122.0, 30.0), RationalTime(57, 30.0)),
              TimeRange(RationalTime(179.0, 30.0), RationalTime(90.0, 30.0)) });

        // Slice again for one frame
        algo::slice(track, RationalTime(179.0, 30.0), true, &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(32.0, 30.0), RationalTime(1, 30.0)),
              TimeRange(RationalTime(33.0, 30.0), RationalTime(57, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(31.0, 30.0)),
              TimeRange(RationalTime(121.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(122.0, 30.0), RationalTime(57, 30.0)),
              TimeRange(RationalTime(179.0, 30.0), RationalTime(90.0, 30.0)) });
    });

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
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite past the clip.
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assertEqual(track->children().size(), 3);
        assert(dynamic_retainer_cast<Gap>(track->children()[1]));
        const RationalTime duration = track->duration();
        assert(duration == RationalTime(72.0, 24.0));
        auto range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)));
    });

    tests.add_test("test_edit_overwrite_1", [] {
        // Create a track with one clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite past the clip.
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assertEqual(track->children().size(), 3);
        assert(dynamic_retainer_cast<Gap>(track->children()[1]));
        const RationalTime duration = track->duration();
        assert(duration == RationalTime(72.0, 24.0));
        auto range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)));
    });

    tests.add_test("test_edit_overwrite_2", [] {
        // Create a track with one clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(1.0, 24.0), RationalTime(100.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite a single frame inside the clip.
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(1.0, 24.0), RationalTime(1.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(42.0, 24.0), RationalTime(1.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime duration = track->duration();
        assert(duration == RationalTime(100.0, 24.0));
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(1.0, 24.0), RationalTime(42.0, 24.0)),
              TimeRange(RationalTime(1.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(44.0, 24.0), RationalTime(57.0, 24.0)) });
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(42.0, 24.0)),
              TimeRange(RationalTime(42.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(43.0, 24.0), RationalTime(57.0, 24.0)) });
    });

    tests.add_test("test_edit_overwrite_3", [] {
        // Create a track with two clips and overwrite a portion of both.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Overwrite both clips.
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_2",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            clip_2,
            track,
            TimeRange(RationalTime(12.0, 24.0), RationalTime(24.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(12.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(36.0, 24.0), RationalTime(12.0, 24.0)) });
    });

    tests.add_test("test_edit_overwrite_4", [] {
        // Create a track with one long clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite one portion of the clip.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(272.0, 24.0), RationalTime(1.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(272.0, 24.0)),
              TimeRange(RationalTime(272.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(
                  RationalTime(273.0, 24.0),
                  RationalTime(431.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(272.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(
                  RationalTime(273.0, 24.0),
                  RationalTime(431.0, 24.0)) });
    });

    tests.add_test("test_edit_overwrite_5", [] {
        // Create a track with one long clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 30.0), RationalTime(704.0, 30.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite one portion of the clip.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(272.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);
        assert(!is_error(error_status));
        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, duration);
        }
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 30.0), RationalTime(272.0, 30.0)),
              TimeRange(RationalTime(272.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(
                  RationalTime(273.0, 30.0),
                  RationalTime(431.0, 30.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 30.0), RationalTime(272.0, 30.0)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(
                  RationalTime(273.0, 30.0),
                  RationalTime(431.0, 30.0)) });

        // Overwrite another portion of the clip.
        SerializableObject::Retainer<Clip> over_2 = new Clip(
            "over_2",
            nullptr,
            TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)));

        algo::overwrite(
            over_2,
            track,
            TimeRange(RationalTime(360.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, duration);
        }
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 30.0), RationalTime(272.0, 30.0)),
              TimeRange(RationalTime(272.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(273.0, 30.0), RationalTime(87.0, 30.0)),
              TimeRange(RationalTime(360.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(
                  RationalTime(361.0, 30.0),
                  RationalTime(343.0, 30.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 30.0), RationalTime(272.0, 30.0)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(273.0, 30.0), RationalTime(87.0, 30.0)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(
                  RationalTime(361.0, 30.0),
                  RationalTime(343.0, 30.0)) });

        // Overwrite the same portion of the clip.
        SerializableObject::Retainer<Clip> over_3 = new Clip(
            "over_3",
            nullptr,
            TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)));

        algo::overwrite(
            over_3,
            track,
            TimeRange(RationalTime(360.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, duration);
        }
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 30.0), RationalTime(272.0, 30.0)),
              TimeRange(RationalTime(272.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(273.0, 30.0), RationalTime(87.0, 30.0)),
              TimeRange(RationalTime(360.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(
                  RationalTime(361.0, 30.0),
                  RationalTime(343.0, 30.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 30.0), RationalTime(272.0, 30.0)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(273.0, 30.0), RationalTime(87.0, 30.0)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(
                  RationalTime(361.0, 30.0),
                  RationalTime(343.0, 30.0)) });
    });

    tests.add_test("test_edit_overwrite_6", [] {
        // Create a track with three clips of different rates.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_2",
            nullptr,
            TimeRange(RationalTime(90.0, 30), RationalTime(90.0, 30)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);

        // Overwrite one portion of the clip.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)));

        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(137.0, 30.0), RationalTime(1.0, 30.0)),
            true,
            nullptr,
            &error_status);

        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(90, 30.0), RationalTime(47.0, 30.0)),
              TimeRange(RationalTime(137.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(138.0, 30.0), RationalTime(42.0, 30.0)),
              TimeRange(RationalTime(180.0, 30.0), RationalTime(90.0, 30.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(47.0, 30.0)),
              TimeRange(RationalTime(0.0, 30.0), RationalTime(1.0, 30.0)),
              TimeRange(RationalTime(48.0, 30.0), RationalTime(42.0, 30.0)),
              TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)) });
    });

    tests.add_test("test_edit_overwrite_7", [] {
        // Create a track with one long clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite past the clip, creating a gap.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(800.0, 24.0), RationalTime(1.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, RationalTime(801.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)),
              TimeRange(RationalTime(704.0, 24.0), RationalTime(96.0, 24.0)),
              TimeRange(RationalTime(800.0, 24.0), RationalTime(1.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(96.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)) });
    });

    tests.add_test("test_edit_overwrite_8", [] {
        // Create a track with one long clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite before the clip, creating a gap.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(-30.0, 24.0), RationalTime(1.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, RationalTime(734.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(1.0, 24.0), RationalTime(29.0, 24.0)),
              TimeRange(RationalTime(30.0, 24.0), RationalTime(704.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(29.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)) });
    });

    tests.add_test("test_edit_overwrite_9", [] {
        // Create a track with one long clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite before the clip, creating a gap.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(100.0, 24.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(-30.0, 24.0), RationalTime(70.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(70.0, 24.0)),
              TimeRange(RationalTime(70.0, 24.0), RationalTime(634.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(70.0, 24.0)),
              TimeRange(RationalTime(70.0, 24.0), RationalTime(634.0, 24.0)) });
    });

    tests.add_test("test_edit_overwrite_10", [] {
        // Create a track with one long clip.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(704.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        // Overwrite before the clip, creating a gap.
        SerializableObject::Retainer<Clip> over_1 = new Clip(
            "over_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(100.0, 24.0)));
        const RationalTime   duration = track->duration();
        OTIO_NS::ErrorStatus error_status;
        algo::overwrite(
            over_1,
            track,
            TimeRange(RationalTime(20.0, 24.0), RationalTime(70.0, 24.0)),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        //assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(70.0, 24.0)),
              TimeRange(RationalTime(90.0, 24.0), RationalTime(614.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(70.0, 24.0)),
              TimeRange(RationalTime(90.0, 24.0), RationalTime(614.0, 24.0)) });
    });

    // Insert at middle of clip_0
    tests.add_test("test_edit_insert_1", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(12.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assertEqual(track->children().size(), 4);
        const RationalTime duration = track->duration();
        assert_duration(duration, RationalTime(60.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(12.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(36.0, 24.0), RationalTime(24.0, 24.0)) });
    });

    // Insert at start of clip_0.
    tests.add_test("test_edit_insert_2", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(0.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assertEqual(track->children().size(), 3);

        const RationalTime duration = track->duration();
        assert_duration(duration, RationalTime(60.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(12.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(36.0, 24.0), RationalTime(24.0, 24.0)) });
    });

    // Insert at start of clip_1 (insert at 0 index).
    tests.add_test("test_edit_insert_3", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(-1.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        assertEqual(track->children().size(), 3);

        const RationalTime duration = track->duration();
        assertEqual(duration, RationalTime(60.0, 24.0));
        auto range = clip_0->trimmed_range_in_parent().value();
        assertEqual(
            range,
            TimeRange(RationalTime(12.0, 24.0), RationalTime(24.0, 24.0)));
        range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            TimeRange(RationalTime(36.0, 24.0), RationalTime(24.0, 24.0)));
        range = insert_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
    });

    // Insert at start of clip_1.
    tests.add_test("test_edit_insert_4", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(24.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime duration = track->duration();
        assert_duration(duration, RationalTime(60.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(36.0, 24.0), RationalTime(24.0, 24.0)) });
    });

    // Insert at end of clip_1 (append at end).
    tests.add_test("test_edit_insert_4", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(48.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime duration = track->duration();
        assert_duration(duration, RationalTime(60.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(24.0, 24.0), RationalTime(24.0, 24.0)),
              TimeRange(RationalTime(48.0, 24.0), RationalTime(12.0, 24.0)) });
    });

    // Insert near the beginning of clip_0.
    tests.add_test("test_edit_insert_5", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(1.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime duration = track->duration();
        assert_duration(duration, RationalTime(60.0, 24.0));
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)),
              TimeRange(RationalTime(1.0, 24.0), RationalTime(12.0, 24.0)),
              TimeRange(RationalTime(13.0, 24.0), RationalTime(23.0, 24.0)),
              TimeRange(RationalTime(36.0, 24.0), RationalTime(24.0, 24.0)) });
    });

    // Insert near the end of clip_1.
    tests.add_test("test_edit_insert_6", [] {
        // Create a track with two clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);

        // Insert in clip 0.
        SerializableObject::Retainer<Clip> insert_1 = new Clip(
            "insert_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(12.0, 24.0)));
        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_1,
            track,
            RationalTime(47.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime duration = track->duration();
        assert_duration(duration, RationalTime(60.0, 24.0));
        assert_track_ranges(
            track,
            {
                TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)),
                TimeRange(RationalTime(24.0, 24.0), RationalTime(23.0, 24.0)),
                TimeRange(RationalTime(47.0, 24.0), RationalTime(12.0, 24.0)),
                TimeRange(RationalTime(59.0, 24.0), RationalTime(1.0, 24.0)),
            });
    });

    // Insert at the end of clip_1.
    tests.add_test("test_edit_insert_7", [] {
        OTIO_NS::ErrorStatus error_status;

        // Create a track with three clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "PSR63_2012-06-02",
            nullptr,
            TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "Dinky_2015-06-11",
            nullptr,
            TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "BART_2021-02-07",
            nullptr,
            TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);
        const RationalTime duration = track->duration();

        track->remove_child(1);

        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, RationalTime(180.0, 30.0));

        assert_clip_ranges(
            track,
            {
                TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
                TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)),
            });

        // Insert at end of clip 2.
        algo::insert(
            clip_1,
            track,
            RationalTime(180.0, 30.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, duration);
        }
        assert_clip_ranges(
            track,
            {
                TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
                TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)),
                TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
            });

        track->remove_child(2);

        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, RationalTime(180.0, 30.0));
        }

        assert_clip_ranges(
            track,
            {
                TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
                TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)),
            });

        // Insert at end of clip 1.
        algo::insert(
            clip_1,
            track,
            RationalTime(90.0, 30.0),
            true,
            nullptr,
            &error_status);

        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, duration);
        }
        assert_clip_ranges(
            track,
            {
                TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
                TimeRange(RationalTime(0.0, 23.98), RationalTime(71.94, 23.98)),
                TimeRange(RationalTime(90.0, 30.0), RationalTime(90.0, 30.0)),
            });
    });

    // Insert at the middle of clip 0
    tests.add_test("test_edit_insert_8", [] {
        OTIO_NS::ErrorStatus error_status;

        // Create a track with three clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "spiderman",
            nullptr,
            TimeRange(
                RationalTime(1575360, 23.976024),
                RationalTime(3809.0, 23.976024)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "spider insert",
            nullptr,
            TimeRange(
                RationalTime(1575360, 23.976024),
                RationalTime(1.0, 23.976024)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);

        debug_track_ranges("START", track);

        // Insert at end of clip 2.
        algo::insert(
            clip_1,
            track,
            RationalTime(141.0, 23.976024),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        // {
        //     const RationalTime new_duration = track->duration();
        //     assert_duration(new_duration, duration);
        // }
        assert_clip_ranges(
            track,
            {
                TimeRange(
                    RationalTime(1575360.0, 23.976024),
                    RationalTime(141.0, 23.976024)),
                TimeRange(
                    RationalTime(1575360, 23.976024),
                    RationalTime(1.0, 23.976024)),
                TimeRange(
                    RationalTime(1575502.0, 23.976024),
                    RationalTime(3668.0, 23.976024)),
            });

        assert_track_ranges(
            track,
            {
                TimeRange(
                    RationalTime(0.0, 23.976024),
                    RationalTime(141.0, 23.976024)),
                TimeRange(
                    RationalTime(141.0, 23.976024),
                    RationalTime(1, 23.976024)),
                TimeRange(
                    RationalTime(142.0, 23.976024),
                    RationalTime(3668.0, 23.976024)),
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
        SerializableObject::Retainer<Gap> clip_0 = new Gap(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
            "gap_0");
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(5.0, 24.0), RationalTime(50.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);
        const RationalTime duration = track->duration();

        OTIO_NS::ErrorStatus error_status;
        algo::trim(
            clip_1,
            RationalTime(5.0, 24.0),
            RationalTime(0.0, 24.0),
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(25.0, 24.0), RationalTime(45.0, 24.0)),
              TimeRange(RationalTime(70.0, 24.0), RationalTime(10.0, 24.0)) });
    });

    // Test trim delta_out right (no change due to clip).
    tests.add_test("test_edit_trim_2", [] {
        // Create a track with one gap and two clips.
        SerializableObject::Retainer<Gap> clip_0 = new Gap(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
            "gap_0");
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(5.0, 24.0), RationalTime(50.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);

        const RationalTime duration = track->duration();

        OTIO_NS::ErrorStatus error_status;
        algo::trim(
            clip_1,
            RationalTime(0.0, 24.0),
            RationalTime(5.0, 24.0),
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(70.0, 24.0), RationalTime(10.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)) });
    });

    // Test trim delta_out left (create a gap)
    tests.add_test("test_edit_trim_3", [] {
        // Create a track with one gap and two clips.
        SerializableObject::Retainer<Gap> clip_0 = new Gap(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
            "gap_0");
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(5.0, 24.0), RationalTime(50.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);

        const RationalTime duration = track->duration();

        OTIO_NS::ErrorStatus error_status;
        algo::trim(
            clip_1,
            RationalTime(0.0, 24.0),
            RationalTime(-5.0, 24.0),
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        const RationalTime new_duration = track->duration();
        assert_duration(new_duration, duration);
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(45.0, 24.0)),
              TimeRange(RationalTime(65.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(70.0, 24.0), RationalTime(10.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(45.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)) });
    });

    // Test ripple
    tests.add_test("test_edit_ripple_1", [] {
        test_edit_ripple(
            RationalTime(10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(35.0, 24.0), RationalTime(20.0, 24.0)) },
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(15.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_ripple_2", [] {
        test_edit_ripple(
            RationalTime(-10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_ripple_3", [] {
        test_edit_ripple(
            RationalTime(0.0, 24.0),
            RationalTime(10.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(35.0, 24.0)),
              TimeRange(RationalTime(55.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(35.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_ripple_4", [] {
        test_edit_ripple(
            RationalTime(0.0, 24.0),
            RationalTime(-10.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(35.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_roll_1", [] {
        test_edit_roll(
            RationalTime(10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(30.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(15.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_roll_2", [] {
        test_edit_roll(
            RationalTime(-10.0, 24.0),
            RationalTime(0.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(15.0, 24.0), RationalTime(35.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(35.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_roll_3", [] {
        test_edit_roll(
            RationalTime(0.0, 24.0),
            RationalTime(10.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(40.0, 24.0)),
              TimeRange(RationalTime(60.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(40.0, 24.0)),
              TimeRange(RationalTime(15.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    tests.add_test("test_edit_roll_4", [] {
        test_edit_roll(
            RationalTime(0.0, 24.0),
            RationalTime(-10.0, 24.0),
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(45.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add longer clip in gap as Fit reference point
    // (creates linearTimeWarp effect).
    tests.add_test("test_edit_fill_1", [] {
        test_edit_fill(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(35.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Fit,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(35.0, 24.0)),
              TimeRange(RationalTime(55.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(35.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add longer clip at gap as Source reference point.
    // Stretches timeline.
    tests.add_test("test_edit_fill_2", [] {
        test_edit_fill(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(35.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Source,
            // Clip in Track Ranges
            {
                TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
                TimeRange(RationalTime(20.0, 24.0), RationalTime(35.0, 24.0)),
                TimeRange(RationalTime(55.0, 24.0), RationalTime(5.0, 24.0)),
            },
            // Clip Ranges
            {
                TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
                TimeRange(RationalTime(0.0, 24.0), RationalTime(35.0, 24.0)),
                TimeRange(RationalTime(20.0, 24.0), RationalTime(5.0, 24.0)),
            });
    });

    // Add equal clip in gap as Source reference point
    tests.add_test("test_edit_fill_3", [] {
        test_edit_fill(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Source,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add shorter clip in gap as Source reference point
    tests.add_test("test_edit_fill_4", [] {
        test_edit_fill(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(5.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Source,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(25.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(10.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add an equal clip (after trim) in gap as
    // Sequence reference point.
    tests.add_test("test_edit_fill_5", [] {
        test_edit_fill(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(35.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(30.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add a longer clip in gap as Sequence reference point
    tests.add_test("test_edit_fill_6", [] {
        test_edit_fill(
            TimeRange(RationalTime(-10.0, 24.0), RationalTime(30.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(35.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(15.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add a shorter clip in gap as Sequence reference point
    tests.add_test("test_edit_fill_7", [] {
        test_edit_fill(
            TimeRange(RationalTime(10.0, 24.0), RationalTime(5.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(25.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(10.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(10.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Add a shorter clip in gap as Sequence reference point
    tests.add_test("test_edit_fill_8", [] {
        test_edit_fill(
            TimeRange(RationalTime(10.0, 24.0), RationalTime(5.0, 24.0)),
            RationalTime(20.0, 24.0),
            ReferencePoint::Sequence,
            // Clip in Track Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(20.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(25.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(20.0, 24.0)) },
            // Clip Ranges
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(20.0, 24.0)),
              TimeRange(RationalTime(10.0, 24.0), RationalTime(5.0, 24.0)),
              TimeRange(RationalTime(10.0, 24.0), RationalTime(25.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(20.0, 24.0)) });
    });

    // Test remove middle clip
    tests.add_test("test_edit_remove_0", [] {
        // Create a track with three clips.
        SerializableObject::Retainer<Clip> clip_0 = new Clip(
            "clip_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_1 = new Clip(
            "clip_1",
            nullptr,
            TimeRange(RationalTime(5.0, 24.0), RationalTime(50.0, 24.0)));
        SerializableObject::Retainer<Clip> clip_2 = new Clip(
            "clip_2",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)));

        SerializableObject::Retainer<Clip> fill_0 = new Clip(
            "fill_0",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip_0);
        track->append_child(clip_1);
        track->append_child(clip_2);

        const RationalTime duration = track->duration();

        OTIO_NS::ErrorStatus error_status;

        // Remove second clip (creates a gap)
        algo::remove(
            track,
            RationalTime(55.0, 24.0),
            true,
            nullptr,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, duration);
        }
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(100.0, 24.0), RationalTime(10.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(5.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)) });

        // Remove second clip (which is now a gap, replacing it with fill_0)
        algo::remove(
            track,
            RationalTime(55.0, 24.0),
            true,
            fill_0,
            &error_status);

        // Asserts.
        assert(!is_error(error_status));
        {
            const RationalTime new_duration = track->duration();
            assert_duration(new_duration, RationalTime(70.0, 24.0));
        }
        assert_track_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(50.0, 24.0), RationalTime(10.0, 24.0)),
              TimeRange(RationalTime(60.0, 24.0), RationalTime(10.0, 24.0)) });
        assert_clip_ranges(
            track,
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(50.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(10.0, 24.0)) });
    });

    // Regression Test: Null Pointer Dereference from Unchecked dynamic_cast
    //
    // The editAlgorithm functions call dynamic_cast<Item*>(item->clone()) and
    // _used to_ immediately dereference the result.
    // SerializableObject::clone() can
    // return nullptr (for example, when the object's metadata contains a
    // cycle, which causes the cloning encoder to error out). When that
    // happens, the dynamic_cast also yields nullptr and the next member call
    // _used to_ dereference the null pointer (denial of service / crash).
    //
    // The tests below construct Items whose metadata contains a cycle (the
    // clip references itself) and exercise each of the four affected call
    // sites. After the fix, the algorithms does not crash and reports a
    // non-OK error status rather than dereferencing nullptr.
    //
    // Helper: make a clip whose clone() will fail because of a metadata cycle.
    auto make_clip_with_cyclic_metadata = [](std::string const& name,
                                             TimeRange const&   source_range)
        -> SerializableObject::Retainer<Clip> {
        SerializableObject::Retainer<Clip> clip =
            new Clip(name, nullptr, source_range);
        // Insert a self-reference in the metadata so that clone() (which
        // round-trips through serialization) detects an OBJECT_CYCLE and
        // returns nullptr.
        clip->metadata()["self"] = SerializableObject::Retainer<>(clip.value);
        // Sanity check: cloning this clip should fail.
        OTIO_NS::ErrorStatus err;
        SerializableObject*  cloned = clip->clone(&err);
        assertTrue(cloned == nullptr);
        assertTrue(is_error(err));
        return clip;
    };

    // overwrite() splits a single clip whose middle is overwritten.
    tests.add_test("test_edit_overwrite_null_clone_safe", [&] {
        auto clip = make_clip_with_cyclic_metadata(
            "cyclic",
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip);

        SerializableObject::Retainer<Clip> insert_clip = new Clip(
            "insert",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(4.0, 24.0)));

        OTIO_NS::ErrorStatus error_status;
        // Overwrite a 4-frame range in the middle of the cyclic clip. This
        // forces the code path that clones items.front() to produce the
        // trailing slice.
        algo::overwrite(
            insert_clip,
            track,
            TimeRange(RationalTime(8.0, 24.0), RationalTime(4.0, 24.0)),
            true,
            nullptr,
            &error_status);
        // Must not crash; must report an error.
        assertTrue(is_error(error_status));
    });

    // insert() splits an existing clip and clones it for the tail.
    tests.add_test("test_edit_insert_null_clone_safe", [&] {
        auto clip = make_clip_with_cyclic_metadata(
            "cyclic",
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip);

        SerializableObject::Retainer<Clip> insert_clip = new Clip(
            "insert",
            nullptr,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(4.0, 24.0)));

        OTIO_NS::ErrorStatus error_status;
        algo::insert(
            insert_clip,
            track,
            RationalTime(12.0, 24.0),
            true,
            nullptr,
            &error_status);
        assertTrue(is_error(error_status));
    });

    // slice() clones an item to create the second slice.
    tests.add_test("test_edit_slice_null_clone_safe", [&] {
        auto clip = make_clip_with_cyclic_metadata(
            "cyclic",
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(clip);

        OTIO_NS::ErrorStatus error_status;
        algo::slice(track, RationalTime(12.0, 24.0), true, &error_status);
        assertTrue(is_error(error_status));
    });

    // fill() clones the source item before placing it on the track.
    tests.add_test("test_edit_fill_null_clone_safe", [&] {
        // Track with a gap so that fill() can find a slot to fill.
        SerializableObject::Retainer<Gap> gap = new Gap(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        SerializableObject::Retainer<Track> track = new Track();
        track->append_child(gap);

        auto clip = make_clip_with_cyclic_metadata(
            "cyclic",
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));

        OTIO_NS::ErrorStatus error_status;
        algo::fill(
            clip,
            track,
            RationalTime(0.0, 24.0),
            ReferencePoint::Sequence,
            &error_status);
        assertTrue(is_error(error_status));
    });

    tests.run(argc, argv);
    return 0;
}
