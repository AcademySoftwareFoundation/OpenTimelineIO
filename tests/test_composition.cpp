// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/composition.h>
#include <opentimelineio/item.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
#include <opentimelineio/transition.h>

#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;

    // test a basic case of find_children
    tests.add_test(
        "test_find_children", [] {
        using namespace otio;
        SerializableObject::Retainer<Composition>  comp  = new Composition;
        SerializableObject::Retainer<Item>  item  = new Item;

        comp->append_child(item);
        OTIO_NS::ErrorStatus err;
        auto result = comp->find_children<>(&err);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, item.value);
    });
    
    // test stack and track correctly calls find_clips from composition parent class
    tests.add_test(
        "test_find_clips", [] {
        using namespace otio;
        SerializableObject::Retainer<Stack> stack = new Stack();
        SerializableObject::Retainer<Track> track = new Track;
        SerializableObject::Retainer<Clip>  clip  = new Clip;
        SerializableObject::Retainer<Transition> transition = new Transition;
        
        stack->append_child(track);
        track->append_child(transition);
        track->append_child(clip);
     
        OTIO_NS::ErrorStatus err;
        auto items = stack->find_clips(&err);
        assertFalse(is_error(err));
        assertEqual(items.size(), 1);
        assertEqual(items[0].value, clip.value);

        items = track->find_clips(&err);
        assertFalse(is_error(err));
        assertEqual(items.size(), 1);
        assertEqual(items[0].value, clip.value);
    });

    tests.run(argc, argv);
    return 0;
}
