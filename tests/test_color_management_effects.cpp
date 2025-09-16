#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/colorManagementEffects.h>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;
    tests.add_test("test_color_management_effects_read", [] {
        using namespace otio;

        otio::ErrorStatus              status;
        SerializableObject::Retainer<> so =
            SerializableObject::from_json_string(
                R"(
            {
                "OTIO_SCHEMA": "Clip.1",
                "media_reference": {
                    "OTIO_SCHEMA": "ExternalReference.1",
                    "target_url": "unit_test_url"
                },
                "effects": [
                    {
                        "OTIO_SCHEMA": "VideoBrightness.1",
                        "name": "brightness",
                        "brightness": 50,
                        "effect_name": "VideoBrightness",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoContrast.1",
                        "name": "contrast",
                        "contrast": 20,
                        "effect_name": "VideoContrast",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoSaturation.1",
                        "name": "saturation",
                        "saturation": 70,
                        "effect_name": "VideoSaturation",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoLightness.1",
                        "name": "lightness",
                        "lightness": 10,
                        "effect_name": "VideoLightness",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoColorTemperature.1",
                        "name": "temperature",
                        "temperature": 6500,
                        "effect_name": "VideoColorTemperature",
                        "enabled": true
                    }
                ]
            })",
                &status);

        if (is_error(status))
            throw std::invalid_argument(status.details);

        const Clip* clip = dynamic_cast<const Clip*>(so.value);
        assertNotNull(clip);

        auto effects = clip->effects();
        assertEqual(effects.size(), 5);

        auto video_brightness = dynamic_cast<const VideoBrightness*>(effects[0].value);
        assertNotNull(video_brightness);
        assertEqual(video_brightness->brightness(), 50);

        auto video_contrast = dynamic_cast<const VideoContrast*>(effects[1].value);
        assertNotNull(video_contrast);
        assertEqual(video_contrast->contrast(), 20);

        auto video_saturation = dynamic_cast<const VideoSaturation*>(effects[2].value);
        assertNotNull(video_saturation);
        assertEqual(video_saturation->saturation(), 70);

        auto video_lightness = dynamic_cast<const VideoLightness*>(effects[3].value);
        assertNotNull(video_lightness);
        assertEqual(video_lightness->lightness(), 10);

        auto video_temperature = dynamic_cast<const VideoColorTemperature*>(effects[4].value);
        assertNotNull(video_temperature);
        assertEqual(video_temperature->temperature(), 6500);
    });

    tests.add_test("test_color_management_effects_write", [] {
        using namespace otio;

        SerializableObject::Retainer<otio::Clip> clip(new otio::Clip(
            "unit_clip",
            new otio::ExternalReference("unit_test_url"),
            std::nullopt,
            otio::AnyDictionary(),
            { new otio::VideoBrightness("brightness", 50),
              new otio::VideoContrast("contrast", 20),
              new otio::VideoSaturation("saturation", 70),
              new otio::VideoLightness("lightness", 10),
              new otio::VideoColorTemperature("temperature", 6500)}));

        auto json = clip.value->to_json_string();

        std::string expected_json = R"({
    "OTIO_SCHEMA": "Clip.2",
    "metadata": {},
    "name": "unit_clip",
    "source_range": null,
    "effects": [
        {
            "OTIO_SCHEMA": "VideoBrightness.1",
            "metadata": {},
            "name": "brightness",
            "effect_name": "VideoBrightness",
            "enabled": true,
            "brightness": 50
        },
        {
            "OTIO_SCHEMA": "VideoContrast.1",
            "metadata": {},
            "name": "contrast",
            "effect_name": "VideoContrast",
            "enabled": true,
            "contrast": 20
        },
        {
            "OTIO_SCHEMA": "VideoSaturation.1",
            "metadata": {},
            "name": "saturation",
            "effect_name": "VideoSaturation",
            "enabled": true,
            "saturation": 70
        },
        {
            "OTIO_SCHEMA": "VideoLightness.1",
            "metadata": {},
            "name": "lightness",
            "effect_name": "VideoLightness",
            "enabled": true,
            "lightness": 10
        },
        {
            "OTIO_SCHEMA": "VideoColorTemperature.1",
            "metadata": {},
            "name": "temperature",
            "effect_name": "VideoColorTemperature",
            "enabled": true,
            "temperature": 6500
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
