// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentime/timeRange.h"
#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/stackAlgorithm.h>

#include <iostream>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test(
        "test_flatten_stack_01", [] {

        RationalTime rt_0_24{0, 24};
        RationalTime rt_150_24{150, 24};
        TimeRange tr_0_150_24{rt_0_24, rt_150_24};

        // all three clips are identical, but placed such that A is over B and
        // has no gap or end over C
        // 0         150          300
        // [    A     ]
        // [    B     |     C     ]
        //
        // should flatten to:
        // [    A     |     C     ]

        SerializableObject::Retainer<Clip> cl_A =
            new Clip("track1_A", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_B =
            new Clip("track1_B", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_C =
            new Clip("track1_C", nullptr, tr_0_150_24);

        SerializableObject::Retainer<Track> tr_over = new Track();
        tr_over->append_child(cl_A);

        SerializableObject::Retainer<Track> tr_under = new Track();
        tr_under->append_child(cl_B);
        tr_under->append_child(cl_C);

        SerializableObject::Retainer<Stack> st = new Stack();
        st->append_child(tr_under);
        st->append_child(tr_over);

        auto result = flatten_stack(st);

        assertEqual(result->children()[0]->name(), std::string("track1_A"));
        assertEqual(result->children().size(), 2);
        assertEqual(result->duration().value(), 300);
    });

    tests.add_test(
        "test_flatten_stack_02", [] {

        RationalTime rt_0_24{0, 24};
        RationalTime rt_150_24{150, 24};
        TimeRange tr_0_150_24{rt_0_24, rt_150_24};

        // all four clips are identical, but placed such that A is over B and
        // has no gap or end over C. The bottom track is also shorter.
        // 0         150          300
        // [    A     ]
        // [    B     |     C     ]
        // [    D     ]
        //
        // should flatten to:
        // [    A     |     C     ]

        SerializableObject::Retainer<Clip> cl_A =
            new Clip("track1_A", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_B =
            new Clip("track1_B", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_C =
            new Clip("track1_C", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_D =
            new Clip("track1_D", nullptr, tr_0_150_24);

        SerializableObject::Retainer<Track> tr_top = new Track();
        tr_top->append_child(cl_A);

        SerializableObject::Retainer<Track> tr_middle = new Track();
        tr_middle->append_child(cl_B);
        tr_middle->append_child(cl_C);

        SerializableObject::Retainer<Track> tr_bottom = new Track();

        tr_bottom->append_child(cl_D);

        SerializableObject::Retainer<Stack> st = new Stack();
        st->append_child(tr_bottom);
        st->append_child(tr_middle);
        st->append_child(tr_top);

        auto result = flatten_stack(st);

        assertEqual(result->children()[0]->name(), std::string("track1_A"));
        assertEqual(result->children().size(), 2);
        assertEqual(result->duration().value(), 300);
    });

    tests.add_test(
        "test_flatten_stack_03", [] {

        RationalTime rt_0_24{0, 24};
        RationalTime rt_150_24{150, 24};
        TimeRange tr_0_150_24{rt_0_24, rt_150_24};

        // all three clips are identical but the middle track is empty
        // 0         150          300
        // [    A     ]
        // []
        // [    B     |     C     ]
        //
        // should flatten to:
        // [    A     |     C     ]

        SerializableObject::Retainer<Clip> cl_A =
            new Clip("track1_A", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_B =
            new Clip("track1_B", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_C =
            new Clip("track1_C", nullptr, tr_0_150_24);

        SerializableObject::Retainer<Track> tr_top = new Track();
        tr_top->append_child(cl_A);

        SerializableObject::Retainer<Track> tr_middle = new Track();

        SerializableObject::Retainer<Track> tr_bottom = new Track();

        tr_bottom->append_child(cl_B);
        tr_bottom->append_child(cl_C);


        SerializableObject::Retainer<Stack> st = new Stack();
        st->append_child(tr_bottom);
        st->append_child(tr_middle);
        st->append_child(tr_top);

        auto result = flatten_stack(st);

        assertEqual(result->children()[0]->name(), std::string("track1_A"));
        assertEqual(result->children().size(), 2);
        assertEqual(result->duration().value(), 300);
    });

    tests.add_test(
        "test_flatten_vector_01", [] {

        RationalTime rt_0_24{0, 24};
        RationalTime rt_150_24{150, 24};
        TimeRange tr_0_150_24{rt_0_24, rt_150_24};

        // all three clips are identical, but placed such that A is over B and
        // has no gap or end over C, tests vector version
        // 0         150          300
        // [    A     ]
        // [    B     |     C     ]
        //
        // should flatten to:
        // [    A     |     C     ]

        SerializableObject::Retainer<Clip> cl_A =
            new Clip("track1_A", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_B =
            new Clip("track1_B", nullptr, tr_0_150_24);
        SerializableObject::Retainer<Clip> cl_C =
            new Clip("track1_C", nullptr, tr_0_150_24);

        SerializableObject::Retainer<Track> tr_over = new Track();
        tr_over->append_child(cl_A);

        SerializableObject::Retainer<Track> tr_under = new Track();
        tr_under->append_child(cl_B);
        tr_under->append_child(cl_C);

        std::vector<Track *> st;
        st.push_back(tr_under);
        st.push_back(tr_over);

        auto result = flatten_stack(st);

        assertEqual(result->children()[0]->name(), std::string("track1_A"));
        assertEqual(result->children().size(), 2);
        assertEqual(result->duration().value(), 300);
    });

    tests.add_test(
        "test_flatten_stack_04", [] {
        using namespace otio;

        otio::RationalTime rt_0_24{0, 24};
        otio::RationalTime rt_150_24{150, 24};
        otio::TimeRange tr_AB_150_24{rt_0_24, rt_150_24};

        otio::TimeRange tr_C_150_24{rt_0_24, otio::RationalTime(300, 24)};

        // A and B are Gaps placed over clip C
        // C should remain uncut
        // 0         150          300
        // [    A     |     B     ]
        // [    C                 ]
        //
        // should flatten to:
        // [    C                 ]

        otio::SerializableObject::Retainer<otio::Gap> cl_A =
            new otio::Gap(tr_AB_150_24, "track1_A");
        otio::SerializableObject::Retainer<otio::Gap> cl_B =
            new otio::Gap(tr_AB_150_24, "track1_B");
        otio::SerializableObject::Retainer<otio::Clip> cl_C =
            new otio::Clip("track2_C", nullptr, tr_C_150_24);

        otio::SerializableObject::Retainer<otio::Track> tr_over =
            new otio::Track();
        tr_over->append_child(cl_A);
        tr_over->append_child(cl_B);

        otio::SerializableObject::Retainer<otio::Track> tr_under =
            new otio::Track();
        tr_under->append_child(cl_C);

        otio::SerializableObject::Retainer<otio::Stack> st =
            new otio::Stack();
        st->append_child(tr_under);
        st->append_child(tr_over);

        auto result = flatten_stack(st);

        assertEqual(result->children().size(), 1);
        assertEqual(result->children()[0]->name(), std::string("track2_C"));
        assertEqual(result->duration().value(), 300);
        assertEqual(st->children().size(), 2);
        assertEqual(dynamic_cast<otio::Track*>(st->children()[0].value)->children().size(), 1);
        assertEqual(dynamic_cast<otio::Track*>(st->children()[1].value)->children().size(), 2);
    });

    tests.add_test(
        "test_flatten_stack_05", [] {
        using namespace otio;

        otio::RationalTime rt_0_24{0, 24};
        otio::RationalTime rt_150_24{150, 24};
        otio::TimeRange tr_150_24{rt_0_24, rt_150_24};

        // A and B are Gaps placed over clips C and D
        // with a cut at the same location
        // 0         150          300
        // [    A     |     B     ]
        // [    C     |     D     ]
        //
        // should flatten to:
        // [    C     |     D     ]

        otio::SerializableObject::Retainer<otio::Gap> cl_A =
            new otio::Gap(tr_150_24, "track1_A");
        otio::SerializableObject::Retainer<otio::Gap> cl_B =
            new otio::Gap(tr_150_24, "track1_B");
        otio::SerializableObject::Retainer<otio::Clip> cl_C =
            new otio::Clip("track2_C", nullptr, tr_150_24);
        otio::SerializableObject::Retainer<otio::Clip> cl_D =
            new otio::Clip("track2_D", nullptr, tr_150_24);


        otio::SerializableObject::Retainer<otio::Track> tr_over =
            new otio::Track();
        tr_over->append_child(cl_A);
        tr_over->append_child(cl_B);

        otio::SerializableObject::Retainer<otio::Track> tr_under =
            new otio::Track();
        tr_under->append_child(cl_C);
        tr_under->append_child(cl_D);

        otio::SerializableObject::Retainer<otio::Stack> st =
            new otio::Stack();
        st->append_child(tr_under);
        st->append_child(tr_over);

        auto result = flatten_stack(st);

        assertEqual(result->children().size(), 2);
        assertEqual(result->children()[0]->name(), std::string("track2_C"));
        assertEqual(result->children()[1]->name(), std::string("track2_D"));
        assertEqual(result->duration().value(), 300);
        assertEqual(st->children().size(), 2);
        assertEqual(dynamic_cast<otio::Track*>(st->children()[0].value)->children().size(), 2);
        assertEqual(dynamic_cast<otio::Track*>(st->children()[1].value)->children().size(), 2);
    });

    tests.run(argc, argv);
    return 0;
}
