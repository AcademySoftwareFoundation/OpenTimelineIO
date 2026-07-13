// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentime/timeRange.h"
#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/stackAlgorithm.h>
#include <opentimelineio/track.h>

#include <iostream>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_flatten_stack_01", [] {
        RationalTime rt_0_24{ 0, 24 };
        RationalTime rt_150_24{ 150, 24 };
        TimeRange    tr_0_150_24{ rt_0_24, rt_150_24 };

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

    tests.add_test("test_flatten_stack_02", [] {
        RationalTime rt_0_24{ 0, 24 };
        RationalTime rt_150_24{ 150, 24 };
        TimeRange    tr_0_150_24{ rt_0_24, rt_150_24 };

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

    tests.add_test("test_flatten_stack_03", [] {
        RationalTime rt_0_24{ 0, 24 };
        RationalTime rt_150_24{ 150, 24 };
        TimeRange    tr_0_150_24{ rt_0_24, rt_150_24 };

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

    tests.add_test("test_flatten_vector_01", [] {
        RationalTime rt_0_24{ 0, 24 };
        RationalTime rt_150_24{ 150, 24 };
        TimeRange    tr_0_150_24{ rt_0_24, rt_150_24 };

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

        std::vector<Track*> st;
        st.push_back(tr_under);
        st.push_back(tr_over);

        auto result = flatten_stack(st);

        assertEqual(result->children()[0]->name(), std::string("track1_A"));
        assertEqual(result->children().size(), 2);
        assertEqual(result->duration().value(), 300);
    });

    tests.run(argc, argv);
    return 0;
}
