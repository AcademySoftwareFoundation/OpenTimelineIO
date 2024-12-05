// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/serializableCollection.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/freezeFrame.h>
#include <opentimelineio/linearTimeWarp.h>
#include <opentimelineio/marker.h>

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
            clip->active_media_reference_key().c_str(),
            Clip::default_media_key);

        assertEqual(media_ref->target_url().c_str(), "unit_test_url");
        assertEqual(media_ref->available_range()->duration().value(), 8);
        assertEqual(media_ref->available_range()->duration().rate(), 24);
        assertEqual(media_ref->available_range()->start_time().value(), 10);
        assertEqual(media_ref->available_range()->start_time().rate(), 24);

        auto mediaReferences = clip->media_references();
        auto found           = mediaReferences.find(Clip::default_media_key);
        assertFalse(found == mediaReferences.end());
    });

    tests.add_test("test_clip_media_representation", [] {
        using namespace otio;

        static constexpr auto time_scalar = 1.5;

        SerializableObject::Retainer<LinearTimeWarp> ltw(new LinearTimeWarp(
            LinearTimeWarp::Schema::name,
            LinearTimeWarp::Schema::name,
            time_scalar));
        std::vector<Effect*> effects = { ltw };

        static constexpr auto red = Marker::Color::red;

        SerializableObject::Retainer<Marker> m(new Marker(
            LinearTimeWarp::Schema::name,
            TimeRange(),
            red));
        std::vector<Marker*> markers = { m };

        static constexpr auto high_quality  = "high_quality";
        static constexpr auto proxy_quality = "proxy_quality";

        SerializableObject::Retainer<MediaReference> media(
            new otio::ExternalReference());

        SerializableObject::Retainer<Clip> clip(new Clip(
            "unit_clip",
            media,
            std::nullopt,
            AnyDictionary(),
            effects,
            markers,
            high_quality));

        assertEqual(clip->active_media_reference_key().c_str(), high_quality);
        assertEqual(clip->media_reference(), media.value);
        assertEqual(clip->active_media_reference_key().c_str(), high_quality);

        SerializableObject::Retainer<MediaReference> ref1(
            new otio::ExternalReference());
        SerializableObject::Retainer<MediaReference> ref2(
            new otio::ExternalReference());
        SerializableObject::Retainer<MediaReference> ref3(
            new otio::ExternalReference());

        clip->set_media_references(
            { { Clip::default_media_key, ref1 },
              { high_quality, ref2 },
              { proxy_quality, ref3 } },
            high_quality);

        assertEqual(clip->media_reference(), ref2.value);

        clip->set_active_media_reference_key(proxy_quality);
        assertEqual(clip->media_reference(), ref3.value);

        clip->set_active_media_reference_key(Clip::default_media_key);
        assertEqual(clip->media_reference(), ref1.value);

        // setting the active reference to a key that does not exist
        // should return an error
        otio::ErrorStatus error;
        clip->set_active_media_reference_key("cloud", &error);
        assertTrue(otio::is_error(error));
        assertEqual(
            error.outcome,
            otio::ErrorStatus::MEDIA_REFERENCES_DO_NOT_CONTAIN_ACTIVE_KEY);
        assertEqual(clip->media_reference(), ref1.value);

        // setting the references that doesn't have the active key should
        // also generate an error
        SerializableObject::Retainer<MediaReference> ref4(
            new otio::ExternalReference());

        otio::ErrorStatus error2;
        clip->set_media_references(
            { { "cloud", ref4 } }, high_quality, &error2);
        assertTrue(otio::is_error(error2));
        assertEqual(
            error2.outcome,
            otio::ErrorStatus::MEDIA_REFERENCES_DO_NOT_CONTAIN_ACTIVE_KEY);

        assertEqual(clip->media_reference(), ref1.value);

        // setting an empty should also generate an error
        otio::ErrorStatus error3;
        clip->set_media_references({ { "", ref4 } }, "", &error3);
        assertTrue(otio::is_error(error3));
        assertEqual(
            error3.outcome,
            otio::ErrorStatus::MEDIA_REFERENCES_CONTAIN_EMPTY_KEY);

        // setting the references and the active key at the same time
        // should work
        clip->set_media_references({ { "cloud", ref4 } }, "cloud");
        assertEqual(clip->media_reference(), ref4.value);

        // basic test for an effect
        assertEqual(clip->effects().size(), effects.size());
        auto effect = dynamic_cast<OTIO_NS::LinearTimeWarp*>(
            clip->effects().front().value);
        assertEqual(effect->time_scalar(), time_scalar);

        // basic test for a marker
        assertEqual(clip->markers().size(), markers.size());
        auto marker = dynamic_cast<OTIO_NS::Marker*>(
            clip->markers().front().value);
        assertEqual(marker->color().c_str(), red);
    });

    tests.run(argc, argv);
    return 0;
}
