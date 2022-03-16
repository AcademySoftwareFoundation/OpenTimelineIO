#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/timeline.h>

#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

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

        otio::SerializableObject::Retainer<otio::Clip> cl(
            new otio::Clip("test_clip"));
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

    tests.add_test("test_clip_v1_to_v2_null", [] {
        using namespace otio;

        otio::ErrorStatus              status;
        SerializableObject::Retainer<> so =
            SerializableObject::from_json_string(
                R"(
            {
                "OTIO_SCHEMA": "Clip.1",
                "media_reference": null
            })",
                &status);

        assertFalse(is_error(status));

        const Clip* clip = dynamic_cast<const Clip*>(so.value);
        assertNotNull(clip);

        const MissingReference* media_ref =
            dynamic_cast<MissingReference*>(clip->media_reference());
        assertNotNull(media_ref);
    });

    tests.add_test("test_clip_v1_to_v2", [] {
        using namespace otio;

        otio::ErrorStatus              status;
        SerializableObject::Retainer<> so =
            SerializableObject::from_json_string(
                R"(
            {
                "OTIO_SCHEMA": "Clip.1",
                "media_reference": {
                    "OTIO_SCHEMA": "ExternalReference.1",
                    "target_url": "unit_test_url",
                    "available_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 8
                        },
                        "start_time": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 10
                        }
                    }
                }
            })",
                &status);

        assertFalse(is_error(status));

        const Clip* clip = dynamic_cast<const Clip*>(so.value);
        assertNotNull(clip);

        const ExternalReference* media_ref =
            dynamic_cast<ExternalReference*>(clip->media_reference());
        assertNotNull(media_ref);
        assertEqual(
            clip->active_media_reference().c_str(),
            Clip::MediaRepresentation::default_media);

        assertEqual(media_ref->target_url().c_str(), "unit_test_url");
        assertEqual(media_ref->available_range()->duration().value(), 8);
        assertEqual(media_ref->available_range()->duration().rate(), 24);
        assertEqual(media_ref->available_range()->start_time().value(), 10);
        assertEqual(media_ref->available_range()->start_time().rate(), 24);

        auto mediaReferences = clip->media_references();
        auto found =
            mediaReferences.find(Clip::MediaRepresentation::default_media);
        assertFalse(found == mediaReferences.end());
    });

    tests.add_test("test_clip_media_representation", [] {
        using namespace otio;

        SerializableObject::Retainer<MediaReference> media(
            new otio::ExternalReference());

        SerializableObject::Retainer<Clip> clip(new Clip(
            "unit_clip",
            media,
            nullopt,
            AnyDictionary(),
            Clip::MediaRepresentation::disk_high_quality_media));

        assertEqual(
            clip->active_media_reference().c_str(),
            Clip::MediaRepresentation::disk_high_quality_media);
        assertEqual(clip->media_reference(), media.value);
        assertEqual(
            clip->active_media_reference().c_str(),
            Clip::MediaRepresentation::disk_high_quality_media);

        SerializableObject::Retainer<MediaReference> ref1(
            new otio::ExternalReference());
        SerializableObject::Retainer<MediaReference> ref2(
            new otio::ExternalReference());
        SerializableObject::Retainer<MediaReference> ref3(
            new otio::ExternalReference());
        SerializableObject::Retainer<MediaReference> ref4(
            new otio::ExternalReference());
        SerializableObject::Retainer<MediaReference> ref5(
            new otio::ExternalReference());

        clip->set_media_references(
            { { Clip::MediaRepresentation::default_media, ref1 },
              { Clip::MediaRepresentation::disk_high_quality_media, ref2 },
              { Clip::MediaRepresentation::disk_proxy_quality_media, ref3 },
              { Clip::MediaRepresentation::cloud_high_quality_media, ref4 },
              { Clip::MediaRepresentation::cloud_proxy_quality_media, ref5 } });

        assertEqual(clip->media_reference(), ref2.value);

        clip->set_active_media_reference(
            Clip::MediaRepresentation::disk_proxy_quality_media);
        assertEqual(clip->media_reference(), ref3.value);

        clip->set_active_media_reference(
            Clip::MediaRepresentation::cloud_high_quality_media);
        assertEqual(clip->media_reference(), ref4.value);

        clip->set_active_media_reference(
            Clip::MediaRepresentation::cloud_proxy_quality_media);
        assertEqual(clip->media_reference(), ref5.value);

        clip->set_active_media_reference(
            Clip::MediaRepresentation::default_media);
        assertEqual(clip->media_reference(), ref1.value);

        clip->set_active_media_reference("dummy");
        assertEqual(clip->media_reference(), nullptr);

        clip->set_media_references({ { "dummy", ref1 } });
        assertEqual(clip->media_reference(), ref1.value);

        clip->set_active_media_reference("dummy2");
        assertEqual(clip->media_reference(), nullptr);
    });

    tests.run(argc, argv);
    return 0;
}
