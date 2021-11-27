#include "tests.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/externalReference.h>

#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_cons", [] {
        std::string         name = "test";
        otime::RationalTime rt(5, 24);
        otime::TimeRange    tr(rt, rt);

        otio::SerializableObject::Retainer<otio::ExternalReference> mr(
            new otio::ExternalReference);
        mr->set_available_range(
            otime::TimeRange(rt, otime::RationalTime(10, 24)));
        mr->set_target_url("/var/tmp/test.mov");

        otio::SerializableObject::Retainer<otio::Clip> cl(new otio::Clip);
        cl->set_name(name);
        cl->set_media_reference(mr);
        cl->set_source_range(tr);
        assertEqual(cl->name(), name);
        assertEqual(cl->source_range().value(), tr);

        std::string encoded = cl->to_json_string();
        otio::SerializableObject::Retainer<otio::SerializableObject> decoded(
            otio::SerializableObject::from_json_string(encoded));
        assertTrue(cl->is_equivalent_to(*decoded));
    });

    tests.add_test("test_ranges", [] {
        otime::TimeRange tr(
            // 1 hour in at 24 fps
            otime::RationalTime(86400, 24),
            otime::RationalTime(200, 24));

        otio::SerializableObject::Retainer<otio::Clip> cl(new otio::Clip("test_clip"));
        otio::SerializableObject::Retainer<otio::ExternalReference> mr(
            new otio::ExternalReference);
        mr->set_target_url("/var/tmp/test.mov");
        mr->set_available_range(tr);
        cl->set_media_reference(mr);
        assertEqual(cl->duration(), cl->trimmed_range().duration());
        assertEqual(cl->duration(), tr.duration());
        assertEqual(cl->trimmed_range(), tr);
        assertEqual(cl->available_range(), tr);

        cl->set_source_range(otime::TimeRange(
            // 1 hour + 100 frames
            otime::RationalTime(86500, 24),
            otime::RationalTime(50, 24)));
        assertNotEqual(cl->duration(), tr.duration());
        assertNotEqual(cl->trimmed_range(), tr);
        assertEqual(cl->duration(), cl->source_range()->duration());
        assertEqual(cl->trimmed_range(), cl->source_range().value());
    });

    tests.run(argc, argv);
    return 0;
}
