// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
#include <opentimelineio/trackAlgorithm.h>
#include <opentimelineio/linearTimeWarp.h>

#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test(
        "test_children_if", [] {
        using namespace otio;
        otio::SerializableObject::Retainer<otio::Clip> cl =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = tr->children_if<otio::Clip>(&err);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl.value);
    });
    tests.add_test(
        "test_children_if_search_range", [] {
        using namespace otio;
        const TimeRange range(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0));
        otio::SerializableObject::Retainer<otio::Clip> cl0 =
            new otio::Clip();
        cl0->set_source_range(range);
        otio::SerializableObject::Retainer<otio::Clip> cl1 =
            new otio::Clip();
        cl1->set_source_range(range);
        otio::SerializableObject::Retainer<otio::Clip> cl2 =
            new otio::Clip();
        cl2->set_source_range(range);
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl0);
        tr->append_child(cl1);
        tr->append_child(cl2);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = tr->children_if<otio::Clip>(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
        result = tr->children_if<otio::Clip>(
            &err,
            TimeRange(RationalTime(24.0, 24.0), RationalTime(24.0, 24.0)));
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl1.value);
        result = tr->children_if<otio::Clip>(
            &err,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)));
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl2.value);
        result = tr->children_if<otio::Clip>(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(48.0, 24.0)));
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
        result = tr->children_if<otio::Clip>(
            &err,
            TimeRange(RationalTime(24.0, 24.0), RationalTime(48.0, 24.0)));
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl1.value);
        assertEqual(result[1].value, cl2.value);
        result = tr->children_if<otio::Clip>(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(72.0, 24.0)));
        assertEqual(result.size(), 3);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
        assertEqual(result[2].value, cl2.value);
    });
    tests.add_test(
        "test_children_if_shallow_search", [] {
        using namespace otio;
        otio::SerializableObject::Retainer<otio::Clip> cl0 =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Clip> cl1 =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Stack> st =
            new otio::Stack();
        st->append_child(cl1);
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl0);
        tr->append_child(st);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = tr->children_if<otio::Clip>(&err, nullopt, true);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
        result = tr->children_if<otio::Clip>(&err, nullopt, false);
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
    });
    tests.add_test(
        "test_track_trimmed_to_range", [] {
        using namespace otio;
        SerializableObject::Retainer<Clip> cl0 =
            new Clip();
        cl0->set_source_range(TimeRange(RationalTime(0,24),
                                        RationalTime(10,24)));
        SerializableObject::Retainer<Clip> cl1 =
            new Clip();
        cl1->set_source_range(TimeRange(RationalTime(20,24),
                                        RationalTime(10,24)));
        SerializableObject::Retainer<Track> tr =
            new Track();
        tr->append_child(cl0);
        tr->append_child(cl1);

        opentimelineio::v1_0::ErrorStatus err;
        auto trimmed_track =
          track_trimmed_to_range(tr,
                                 TimeRange(RationalTime(5,24),
                                           RationalTime(7,24)),
                                 &err);
        assertFalse(is_error(err));

        assertEqual(trimmed_track->children().size(), 2);
        const auto cl0_trimmed = dynamic_cast<Clip*>(trimmed_track->children().at(0).value);
        const auto cl1_trimmed = dynamic_cast<Clip*>(trimmed_track->children().at(1).value);
        const auto cl0_trimmed_range = cl0_trimmed->trimmed_range();
        const auto cl1_trimmed_range = cl1_trimmed->trimmed_range();
        assertEqual(cl0_trimmed_range,
                    TimeRange(RationalTime(5,24),
                              RationalTime(5,24)));
        assertEqual(cl1_trimmed_range,
                    TimeRange(RationalTime(20,24),
                              RationalTime(2,24)));
    });
    tests.add_test(
        "test_track_trimmed_to_range_with_timewarp", [] {
        using namespace otio;
        SerializableObject::Retainer<Clip> cl0 =
            new Clip();
        cl0->set_source_range(TimeRange(RationalTime(0,24),
                                        RationalTime(10,24)));
        SerializableObject::Retainer<LinearTimeWarp> tw0 =
          new LinearTimeWarp("tw0", "", 0.51);
        cl0->effects().push_back(dynamic_retainer_cast<Effect>(tw0));
        SerializableObject::Retainer<Clip> cl1 =
            new Clip();
        cl1->set_source_range(TimeRange(RationalTime(20,24),
                                        RationalTime(10,24)));
        SerializableObject::Retainer<LinearTimeWarp> tw1 =
          new LinearTimeWarp("tw1", "", 0.51);
        cl1->effects().push_back(dynamic_retainer_cast<Effect>(tw1));
        SerializableObject::Retainer<Track> tr =
            new Track();
        tr->append_child(cl0);
        tr->append_child(cl1);

        opentimelineio::v1_0::ErrorStatus err;

        // Try IgnoreTimeEffects
        auto trimmed_track =
          track_trimmed_to_range(tr,
                                 TimeRange(RationalTime(5,24),
                                           RationalTime(7,24)),
                                 &err,
                                 IgnoreTimeEffects);
        assertFalse(is_error(err));

        assertEqual(trimmed_track->children().size(), 2);
        auto cl0_trimmed = dynamic_cast<Clip*>(trimmed_track->children().at(0).value);
        auto cl1_trimmed = dynamic_cast<Clip*>(trimmed_track->children().at(1).value);
        auto cl0_trimmed_range = cl0_trimmed->trimmed_range();
        auto cl1_trimmed_range = cl1_trimmed->trimmed_range();
        assertEqual(cl0_trimmed_range,
                    TimeRange(RationalTime(5,24),
                              RationalTime(5,24)));
        auto tw = dynamic_cast<LinearTimeWarp*>(cl0_trimmed->effects()[0].value);
        assertEqual(tw->time_scalar(), 0.51);
        assertEqual(cl1_trimmed_range,
                    TimeRange(RationalTime(20,24),
                              RationalTime(2,24)));
        tw = dynamic_cast<LinearTimeWarp*>(cl1_trimmed->effects()[0].value);
        assertEqual(tw->time_scalar(), 0.51);

        // Try HonorTimeEffectsExactly
        auto trimmed_track2 =
          track_trimmed_to_range(tr,
                                 TimeRange(RationalTime(5,24),
                                           RationalTime(7,24)),
                                 &err,
                                 HonorTimeEffectsExactly);
        assertFalse(is_error(err));

        assertEqual(trimmed_track2->children().size(), 2);
        cl0_trimmed = dynamic_cast<Clip*>(trimmed_track2->children().at(0).value);
        cl1_trimmed = dynamic_cast<Clip*>(trimmed_track2->children().at(1).value);
        cl0_trimmed_range = cl0_trimmed->trimmed_range();
        cl1_trimmed_range = cl1_trimmed->trimmed_range();
        assertEqual(cl0_trimmed_range,
                    TimeRange(RationalTime(2.55,24),
                              RationalTime(5,24)));
        tw = dynamic_cast<LinearTimeWarp*>(cl0_trimmed->effects()[0].value);
        assertEqual(tw->time_scalar(), 0.51);
        assertEqual(cl1_trimmed_range,
                    TimeRange(RationalTime(20,24),
                              RationalTime(2,24)));
        tw = dynamic_cast<LinearTimeWarp*>(cl1_trimmed->effects()[0].value);
        assertEqual(tw->time_scalar(), 0.51);

        // Try HonorTimeEffectsWithSnapping
        auto trimmed_track3 =
          track_trimmed_to_range(tr,
                                 TimeRange(RationalTime(5,24),
                                           RationalTime(7,24)),
                                 &err,
                                 HonorTimeEffectsWithSnapping);
        assertFalse(is_error(err));

        assertEqual(trimmed_track3->children().size(), 2);
        cl0_trimmed = dynamic_cast<Clip*>(trimmed_track3->children().at(0).value);
        cl1_trimmed = dynamic_cast<Clip*>(trimmed_track3->children().at(1).value);
        cl0_trimmed_range = cl0_trimmed->trimmed_range();
        cl1_trimmed_range = cl1_trimmed->trimmed_range();
        assertEqual(cl0_trimmed_range,
                    TimeRange(RationalTime(2,24),
                              RationalTime(5,24)));
        tw = dynamic_cast<LinearTimeWarp*>(cl1_trimmed->effects()[0].value);
        assertEqual(tw->time_scalar(), 0.5);
        assertEqual(cl1_trimmed_range,
                    TimeRange(RationalTime(20,24),
                              RationalTime(2,24)));
        tw = dynamic_cast<LinearTimeWarp*>(cl1_trimmed->effects()[0].value);
        assertEqual(tw->time_scalar(), 0.5);
    });
    tests.run(argc, argv);
    return 0;
}
