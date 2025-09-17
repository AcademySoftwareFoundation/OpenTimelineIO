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
                        "OTIO_SCHEMA": "VideoRoundedCorners.1",
                        "name": "roundedCorners",
                        "radius": 80,
                        "effect_name": "VideoRoundedCorners",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoFlip.1",
                        "name": "flip",
                        "flip_horizontally": true,
                        "flip_vertically": false,
                        "effect_name": "VideoFlip",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoMask.1",
                        "name": "mask",
                        "mask_type": "REMOVE",
                        "mask_url": "mask_url",
                        "effect_name": "VideoMaskRemove",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoMask.1",
                        "name": "mask",
                        "mask_type": "REPLACE",
                        "mask_url": "mask_url",
                        "effect_name": "VideoMaskReplace",
                        "mask_replacement_url": "mask_replacement_url",
                        "enabled": true
                    },
                    {
                        "OTIO_SCHEMA": "VideoMask.1",
                        "name": "mask",
                        "mask_type": "BLUR",
                        "mask_url": "mask_url",
                        "effect_name": "VideoMaskBlur",
                        "blur_radius": 10.1,
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
        assertEqual(effects.size(), 9);

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

        auto video_rounded_corners = dynamic_cast<const VideoRoundedCorners*>(effects[4].value);
        assertNotNull(video_rounded_corners);
        assertEqual(video_rounded_corners->radius(), 80);

        auto video_flip = dynamic_cast<const VideoFlip*>(effects[5].value);
        assertNotNull(video_flip);
        assertEqual(video_flip->flip_horizontally(), true);
        assertEqual(video_flip->flip_vertically(), false);

        auto video_mask_remove = dynamic_cast<const VideoMask*>(effects[6].value);
        assertNotNull(video_mask_remove);
        assertEqual(video_mask_remove->mask_type(), std::string(VideoMask::MaskType::remove));
        assertEqual(video_mask_remove->mask_url(), std::string("mask_url"));

        auto video_mask_replace = dynamic_cast<const VideoMask*>(effects[7].value);
        assertNotNull(video_mask_replace);
        assertEqual(video_mask_replace->mask_type(), std::string(VideoMask::MaskType::replace));
        assertEqual(video_mask_replace->mask_url(), std::string("mask_url"));
        assertEqual(video_mask_replace->mask_replacement_url().value(), std::string("mask_replacement_url"));

        auto video_mask_blur = dynamic_cast<const VideoMask*>(effects[8].value);
        assertNotNull(video_mask_blur);
        assertEqual(video_mask_blur->mask_type(), std::string(VideoMask::MaskType::blur));
        assertEqual(video_mask_blur->mask_url(), std::string("mask_url"));
        assertEqual(video_mask_blur->blur_radius().value(), 10.1);
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
              new otio::VideoRoundedCorners("roundedCorners",80),
              new otio::VideoFlip("flip", true, false),
              new otio::VideoMask("mask", otio::VideoMask::MaskType::remove, "mask_url")
            }));

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
            "OTIO_SCHEMA": "VideoRoundedCorners.1",
            "metadata": {},
            "name": "roundedCorners",
            "effect_name": "VideoRoundedCorners",
            "enabled": true,
            "radius": 80
        },
        {
            "OTIO_SCHEMA": "VideoFlip.1",
            "metadata": {},
            "name": "flip",
            "effect_name": "VideoFlip",
            "enabled": true,
            "flip_horizontally": true,
            "flip_vertically": false
        },
        {
            "OTIO_SCHEMA": "VideoMask.1",
            "metadata": {},
            "name": "mask",
            "effect_name": "VideoMask",
            "enabled": true,
            "mask_type": "REMOVE",
            "mask_url": "mask_url"
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
