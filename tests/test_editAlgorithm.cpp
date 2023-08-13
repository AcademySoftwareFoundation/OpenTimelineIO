// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/editAlgorithm.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/track.h>

#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

using otime::RationalTime;
using otime::TimeRange;

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

namespace {

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

    // Slice.
    otio::ErrorStatus error_status;
    edit_slice(track, slice_time, &error_status);

    // Asserts.
    assert(!otio::is_error(error_status));
    assertEqual(track->children().size(), slice_ranges.size());
    std::vector<otio::TimeRange> ranges;
    for (const auto& child: track->children())
    {
        ranges.push_back(track->trimmed_range_of_child(child).value());
    }
    assertEqual(slice_ranges, ranges);
}

} // namespace

int
main(int argc, char** argv)
{
    Tests tests;
    tests.add_test("test_edit_slice", [] {
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
            { TimeRange(RationalTime(0.0, 24.0), RationalTime(0.0, 24.0)),
              TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)) });

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
        otio::edit_overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)),
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
                otio::RationalTime(72.0, 24.0)));
        otio::SerializableObject::Retainer<otio::Track> track =
            new otio::Track();
        track->append_child(clip_0);

        // Overwrite a portion inside the clip.
        otio::SerializableObject::Retainer<otio::Clip> clip_1 = new otio::Clip(
            "clip_1",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        otio::ErrorStatus error_status;
        otio::edit_overwrite(
            clip_1,
            track,
            TimeRange(RationalTime(24.0, 24.0), RationalTime(24.0, 24.0)),
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime duration = track->duration();
        assert(duration == otio::RationalTime(72.0, 24.0));
        assertEqual(track->children().size(), 3);
        auto item =
            otio::dynamic_retainer_cast<otio::Item>(track->children()[0]);
        assert(item);
        auto range = item->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        item = otio::dynamic_retainer_cast<otio::Item>(track->children()[1]);
        assert(item);
        range = item->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(24.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        item = otio::dynamic_retainer_cast<otio::Item>(track->children()[2]);
        assert(item);
        range = item->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(48.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
    });

    tests.add_test("test_edit_overwrite_2", [] {
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

        // Overwrite both clips.
        otio::SerializableObject::Retainer<otio::Clip> clip_2 = new otio::Clip(
            "clip_2",
            nullptr,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        const RationalTime duration = track->duration();
        otio::ErrorStatus  error_status;
        otio::edit_overwrite(
            clip_2,
            track,
            TimeRange(RationalTime(12.0, 24.0), RationalTime(24.0, 24.0)),
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        const RationalTime new_duration = track->duration();
        assertEqual(duration, new_duration);
        auto range = clip_0->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(36.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        range = clip_2->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(12.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
    });

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
        otio::edit_insert(
            insert_1,
            track,
            RationalTime(12.0, 24.0),
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 4);
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        auto range = clip_0->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        range = insert_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(12.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(36.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
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
        otio::edit_insert(
            insert_1,
            track,
            RationalTime(0.0, 24.0),
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 3);
        
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        auto range = insert_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
        range = clip_0->trimmed_range_in_parent().value();
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
    });
    
    // Insert at end of clip_1 (append at end).
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
        otio::edit_insert(
            insert_1,
            track,
            RationalTime(48.0, 24.0),
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
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(24.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        range = insert_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(48.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
    });
    
    // Insert near the beginning of clip_0.
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
        otio::edit_insert(
            insert_1,
            track,
            RationalTime(1.0, 24.0),
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 4);
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        auto range = clip_0->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(1.0, 24.0)));
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
                otio::RationalTime(1.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
    });
    
    // Insert near the end of clip_1 (append at end).
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
        otio::edit_insert(
            insert_1,
            track,
            RationalTime(47.0, 24.0),
            &error_status);

        // Asserts.
        assert(!otio::is_error(error_status));
        assertEqual(track->children().size(), 4);
        const RationalTime duration = track->duration();
        assertEqual(duration, otime::RationalTime(60.0,24.0));
        auto range = clip_0->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(0.0, 24.0),
                otio::RationalTime(24.0, 24.0)));
        range = clip_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(24.0, 24.0),
                otio::RationalTime(23.0, 24.0)));
        range = insert_1->trimmed_range_in_parent().value();
        assertEqual(
            range,
            otio::TimeRange(
                otio::RationalTime(47.0, 24.0),
                otio::RationalTime(12.0, 24.0)));
    });
    
    tests.run(argc, argv);
    return 0;
}
