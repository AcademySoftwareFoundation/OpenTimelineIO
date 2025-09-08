#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/transformEffects.h>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;
    tests.add_test("test_video_transform_read", [] {
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
                        "OTIO_SCHEMA": "VideoScale.1",
                        "name": "scale",
                        "width": 100,
                        "height": 120,
                        "effect_name": "VideoScale",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoPosition.1",
                        "name": "position",
                        "x": 10,
                        "y": 20,
                        "effect_name": "VideoPosition",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoRotate.1",
                        "name": "rotate",
                        "angle": 45.5,
                        "effect_name": "VideoRotate",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoCrop.1",
                        "name": "crop",
                        "left": 5,
                        "right": 6,
                        "top": 7,
                        "bottom": 8,
                        "effect_name": "VideoCrop",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoFlip.1",
                        "name": "flip",
                        "flip_horizontally": true,
                        "flip_vertically": false,
                        "effect_name": "VideoFlip",
                        "enabled": true
                    }
                ]
            })",
                &status);

        assertFalse(is_error(status));

        const Clip* clip = dynamic_cast<const Clip*>(so.value);
        assertNotNull(clip);

        auto effects = clip->effects();
        assertEqual(effects.size(), 5);

        auto video_scale = dynamic_cast<const VideoScale*>(effects[0].value);
        assertNotNull(video_scale);
        assertEqual(video_scale->width(), 100);
        assertEqual(video_scale->height(), 120);

        auto video_position = dynamic_cast<const VideoPosition*>(effects[1].value);
        assertNotNull(video_position);
        assertEqual(video_position->x(), 10);
        assertEqual(video_position->y(), 20);

        auto video_rotate = dynamic_cast<const VideoRotate*>(effects[2].value);
        assertNotNull(video_rotate);
        assertEqual(video_rotate->angle(), 45.5);

        auto video_crop = dynamic_cast<const VideoCrop*>(effects[3].value);
        assertNotNull(video_crop);
        assertEqual(video_crop->left(), 5);
        assertEqual(video_crop->right(), 6);
        assertEqual(video_crop->top(), 7);
        assertEqual(video_crop->bottom(), 8);

        auto video_flip = dynamic_cast<const VideoFlip*>(effects[4].value);
        assertNotNull(video_flip);
        assertEqual(video_flip->flip_horizontally(), true);
        assertEqual(video_flip->flip_vertically(), false);
    });

    tests.add_test("test_video_transform_write", [] {
        using namespace otio;

        SerializableObject::Retainer<otio::Clip> clip(new otio::Clip(
            "unit_clip",
            new otio::ExternalReference("unit_test_url"),
            std::nullopt,
            otio::AnyDictionary(),
            { new otio::VideoScale("scale", 100, 120),
              new otio::VideoPosition("position", 10, 20),
              new otio::VideoRotate("rotate", 40.5),
              new otio::VideoCrop("crop", 1, 2, 3, 4),
              new otio::VideoFlip("flip", true, false) }));

        auto json = clip.value->to_json_string();

        std::string expected_json = R"({
    "OTIO_SCHEMA": "Clip.2",
    "metadata": {},
    "name": "unit_clip",
    "source_range": null,
    "effects": [
        {
            "OTIO_SCHEMA": "VideoScale.1",
            "metadata": {},
            "name": "scale",
            "effect_name": "VideoScale",
            "enabled": true,
            "width": 100,
            "height": 120
        },
        {
            "OTIO_SCHEMA": "VideoPosition.1",
            "metadata": {},
            "name": "position",
            "effect_name": "VideoPosition",
            "enabled": true,
            "x": 10,
            "y": 20
        },
        {
            "OTIO_SCHEMA": "VideoRotate.1",
            "metadata": {},
            "name": "rotate",
            "effect_name": "VideoRotate",
            "enabled": true,
            "angle": 40.5
        },
        {
            "OTIO_SCHEMA": "VideoCrop.1",
            "metadata": {},
            "name": "crop",
            "effect_name": "VideoCrop",
            "enabled": true,
            "left": 1,
            "right": 2,
            "top": 3,
            "bottom": 4
        },
        {
            "OTIO_SCHEMA": "VideoFlip.1",
            "metadata": {},
            "name": "flip",
            "effect_name": "VideoFlip",
            "enabled": true,
            "flip_horizontally": true,
            "flip_vertically": false
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
