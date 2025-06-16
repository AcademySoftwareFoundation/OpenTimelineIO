#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/volumeEffects.h>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;
    tests.add_test("test_audio_volume_read", [] {
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
                },
                "effects": [
                    {
                        "OTIO_SCHEMA": "AudioVolume.1",
                        "name": "volume",
                        "gain": 0.5,
                        "effect_name": "AudioVolume",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "AudioFade.1",
                        "name": "fade",
                        "fade_in": false,
                        "start_time": 1.5,
                        "duration": 5.0,
                        "effect_name": "AudioFade",
                        "enabled": true
                    }
                ]
            })",
                &status);

        assertFalse(is_error(status));

        const Clip* clip = dynamic_cast<const Clip*>(so.value);
        assertNotNull(clip);

        auto effects = clip->effects();
        assertEqual(effects.size(), 2);

        auto audio_volume = dynamic_cast<const AudioVolume*>(effects[0].value);
        assertNotNull(audio_volume);
        assertEqual(audio_volume->gain(), 0.5);

        auto audio_fade = dynamic_cast<const AudioFade*>(effects[1].value);
        assertNotNull(audio_fade);
        assertEqual(audio_fade->fade_in(), false);
        assertEqual(audio_fade->start_time(), 1.5);
        assertEqual(audio_fade->duration(), 5.0);
    });

    tests.add_test("test_audio_volume_write", [] {
        using namespace otio;

        SerializableObject::Retainer<otio::Clip> clip(new otio::Clip(
            "unit_clip",
            new otio::ExternalReference("unit_test_url"),
            std::nullopt,
            otio::AnyDictionary(),
            { new otio::AudioVolume("volume", 0.75),
              new otio::AudioFade("fade", true, 2.0, 10.5)}));

        auto json = clip.value->to_json_string();

        std::string expected_json = R"({
    "OTIO_SCHEMA": "Clip.2",
    "metadata": {},
    "name": "unit_clip",
    "source_range": null,
    "effects": [
        {
            "OTIO_SCHEMA": "AudioVolume.1",
            "metadata": {},
            "name": "volume",
            "effect_name": "AudioVolume",
            "enabled": true,
            "gain": 0.75
        },
        {
            "OTIO_SCHEMA": "AudioFade.1",
            "metadata": {},
            "name": "fade",
            "effect_name": "AudioFade",
            "enabled": true,
            "fade_in": true,
            "start_time": 2.0,
            "duration": 10.5
        }
    ],
    "markers": [],
    "enabled": true,
    "media_references": {
        "DEFAULT_MEDIA": {
            "OTIO_SCHEMA": "ExternalReference.1",
            "metadata": {},
            "name": "",
            "available_range": null,
            "available_image_bounds": null,
            "target_url": "unit_test_url"
        }
    },
    "active_media_reference_key": "DEFAULT_MEDIA"
})";

        assertEqual(json, expected_json);

    });

    tests.run(argc, argv);
    return 0;
}
