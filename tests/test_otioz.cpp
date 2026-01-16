// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include "opentimelineio/bundle.h"
#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/fileUtils.h"
#include "opentimelineio/imageSequenceReference.h"
#include "opentimelineio/missingReference.h"
#include "opentimelineio/urlUtils.h"

#include <iomanip>
#include <iostream>
#include <sstream>

namespace otime  = opentime::OPENTIME_VERSION;
namespace otio   = opentimelineio::OPENTIMELINEIO_VERSION;
namespace bundle = opentimelineio::OPENTIMELINEIO_VERSION::bundle;

int
main(int argc, char** argv)
{
    Tests tests;

    // Sample data paths.
    std::filesystem::path const sample_data_dir =
        std::filesystem::u8path(OTIO_TESTS_DIR) / "sample_data";
    std::string const screening_example_path = otio::to_unix_separators(
        (sample_data_dir / "screening_example.otio").u8string());

    // Sample media paths.
    std::string const media_example_path_rel     = "OpenTimelineIO@3xDark.png";
    std::string const media_example_path_url_rel = otio::to_unix_separators(
        otio::url_from_filepath(media_example_path_rel));
    std::string const media_example_path_abs = otio::to_unix_separators(
        (sample_data_dir / "OpenTimelineIO@3xLight.png").u8string());
    std::string const media_example_path_url_abs = otio::to_unix_separators(
        otio::url_from_filepath(media_example_path_abs));

    // Test timeline.
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
        dynamic_cast<otio::Timeline*>(
            otio::Timeline::from_json_file(screening_example_path)));

    // Convert to contrived local references.
    bool last_rel = false;
    for (auto cl: timeline->find_clips())
    {
        // Vary the relative and absolute paths, make sure that both work.
        std::string const next_rel = last_rel ? media_example_path_url_rel
                                              : media_example_path_url_abs;
        last_rel                   = !last_rel;
        cl->set_media_reference(new otio::ExternalReference(next_rel));
    }

    tests.add_test(
        "test_media_size",
        [sample_data_dir,
         media_example_path_rel,
         media_example_path_abs,
         timeline]
        {
            bundle::WriteOptions options;
            options.parent_path = sample_data_dir.u8string();
            size_t const size   = bundle::get_media_size(timeline, options);
            size_t const size_compare =
                std::filesystem::file_size(
                    sample_data_dir / media_example_path_rel)
                + std::filesystem::file_size(media_example_path_abs);
            assertEqual(size, size_compare);
        });

    tests.add_test(
        "test_not_a_file_error",
        [sample_data_dir,
         timeline]
        {
            otio::SerializableObject::Retainer<otio::Timeline> clone(
                dynamic_cast<otio::Timeline*>(timeline->clone()));
            for (auto cl : clone->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    // Write with a non-file scheme.
                    er->set_target_url("http://not.a.file.com");
                }
            }

            std::filesystem::path const temp_dir  = otio::create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otioz";
            otio::ErrorStatus error;
            assertFalse(bundle::to_otioz(
                clone,
                temp_file.u8string(),
                bundle::WriteOptions(),
                &error));
            std::cout << "ERROR: " << error.details << std::endl;
            assertTrue(otio::is_error(error));
        });

    tests.add_test(
        "test_colliding_basename",
        [sample_data_dir, media_example_path_abs, timeline]
        {
            std::filesystem::path const temp_dir = otio::create_temp_dir();

            std::filesystem::path const colliding_file =
                temp_dir / std::filesystem::u8path(media_example_path_abs).
                filename();
            std::filesystem::copy_file(media_example_path_abs, colliding_file);

            otio::SerializableObject::Retainer<otio::Timeline> clone(
                dynamic_cast<otio::Timeline*>(timeline->clone()));
            if (auto er = dynamic_cast<otio::ExternalReference*>(
                    clone->find_clips()[0]->media_reference()))
            {
                er->set_target_url(otio::url_from_filepath(colliding_file.u8string()));
            }

            std::filesystem::path const temp_file = temp_dir / "test.otioz";
            bundle::WriteOptions options;
            options.parent_path = sample_data_dir.u8string();
            otio::ErrorStatus error;
            assertFalse(bundle::to_otioz(
                clone,
                temp_file.u8string(),
                options,
                &error));
            std::cout << "ERROR: " << error.details << std::endl;
            assertTrue(otio::is_error(error));
        });

    tests.add_test(
        "test_round_trip",
        [sample_data_dir, timeline]
        {
            std::filesystem::path const temp_dir  = otio::create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otioz";
            bundle::WriteOptions options;
            options.parent_path = sample_data_dir.u8string();
            assertTrue(bundle::to_otioz(
                timeline,
                temp_file.u8string(),
                options));

            auto result = bundle::from_otioz(temp_file.u8string());

            for (auto cl : result->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    // Ensure that UNIX style paths are used, so that bundles
                    // created on Windows are compatible with ones created on UNIX.
                    std::string const windows("media\\");
                    assertNotEqual(
                        otio::filepath_from_url(er->target_url())
                            .substr(windows.size()),
                        windows);
                }
            }

            // Clone the input and conform the media references to what they
            // should be in the output.
            otio::SerializableObject::Retainer<otio::Timeline> clone(
                dynamic_cast<otio::Timeline*>(timeline->clone()));
            for (auto cl : clone->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    std::string const file =
                        std::filesystem::path(
                            otio::filepath_from_url(er->target_url()))
                            .filename()
                            .u8string();
                    std::string const url = otio::url_from_filepath(
                        (std::filesystem::u8path(bundle::media_dir) / file)
                            .u8string());
                    er->set_target_url(url);
                }
            }

            assertEqual(result->to_json_string(), clone->to_json_string());
        });

    tests.add_test(
        "test_round_trip_with_extraction",
        [sample_data_dir, timeline]
        {
            std::filesystem::path const temp_dir  = otio::create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otioz";
            bundle::WriteOptions        write_options;
            write_options.parent_path = sample_data_dir.u8string();
            assertTrue(bundle::to_otioz(
                timeline,
                temp_file.u8string(),
                write_options));

            bundle::OtiozReadOptions    read_options;
            std::filesystem::path const output_path = temp_dir / "extract";
            read_options.extract_path = output_path.u8string();
            auto result = bundle::from_otioz(
                temp_file.u8string(),
                read_options);

            // Make sure that all the references are ExternalReference.
            for (auto cl : result->find_clips())
            {
                assertTrue(dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()));
            }

            // Clone the input and conform the media references to what they
            // should be in the output.
            otio::SerializableObject::Retainer<otio::Timeline> clone(
                dynamic_cast<otio::Timeline*>(timeline->clone()));
            for (auto cl: clone->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    std::string const file =
                        std::filesystem::path(
                            otio::filepath_from_url(er->target_url()))
                            .filename()
                            .u8string();
                    std::string const url = otio::url_from_filepath(
                        (std::filesystem::u8path(bundle::media_dir) / file)
                            .u8string());
                    er->set_target_url(url);
                }
            }
            assertEqual(result->to_json_string(), clone->to_json_string());

            // Check the version file exists.
            assertTrue(
                std::filesystem::exists(output_path / bundle::version_file));

            // Check the content file exists.
            assertTrue(
                std::filesystem::exists(output_path / bundle::otio_file));

            // Check the media directory exists.
            assertTrue(
                std::filesystem::exists(output_path / bundle::media_dir));

            // Check the media files exist.
            for (auto cl: clone->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    std::string const file =
                        otio::filepath_from_url(er->target_url());
                    assertTrue(std::filesystem::exists(output_path / file));
                }
            }
        });

    tests.add_test(
        "test_round_trip_with_extraction_no_media",
        [sample_data_dir, timeline]
        {
            std::filesystem::path const temp_dir  = otio::create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otioz";
            bundle::WriteOptions        write_options;
            write_options.parent_path = sample_data_dir.u8string();
            write_options.media_policy = bundle::MediaReferencePolicy::AllMissing;
            assertTrue(bundle::to_otioz(
                timeline,
                temp_file.u8string(),
                write_options));

            bundle::OtiozReadOptions    read_options;
            std::filesystem::path const output_path = temp_dir / "extract";
            read_options.extract_path = output_path.u8string();
            auto result = bundle::from_otioz(
                temp_file.u8string(),
                read_options);

            // Check the version file exists.
            assertTrue(
                std::filesystem::exists(output_path / bundle::version_file));

            // Check the content file exists.
            assertTrue(
                std::filesystem::exists(output_path / bundle::otio_file));

            // Should be all missing references.
            for (auto cl: result->find_clips())
            {
                assertTrue(dynamic_cast<otio::MissingReference*>(
                    cl->media_reference()));

                auto const& metadata = cl->media_reference()->metadata();
                assertTrue(
                    metadata.find("original_target_url") != metadata.end());
            }
        });

    tests.add_test(
        "test_round_trip_with_sequence",
        [sample_data_dir, media_example_path_rel]
        {
            // Create an image sequence.
            std::filesystem::path const temp_dir = otio::create_temp_dir();
            std::string const name_prefix = "sequence.";
            std::string const name_suffix = ".png";
            int const frame_zero_padding = 4;
            int const sequence_frames = 10;
            for (int frame = 0; frame < sequence_frames; ++frame)
            {
                std::stringstream ss;
                ss << name_prefix <<
                    std::setfill('0') << std::setw(frame_zero_padding) <<
                    frame <<
                    name_suffix;
                std::filesystem::copy(
                    sample_data_dir / media_example_path_rel,
                    temp_dir / ss.str());
            }

            // Create a timeline with an image sequence reference.
            otio::SerializableObject::Retainer<otio::Timeline> timeline(
                new otio::Timeline);
            auto track = new otio::Track;
            timeline->tracks()->append_child(track);
            auto isr = new otio::ImageSequenceReference(
                "",
                name_prefix,
                name_suffix,
                0,
                1,
                24.0,
                frame_zero_padding,
                otio::ImageSequenceReference::MissingFramePolicy::error,
                otio::TimeRange(0.0, sequence_frames, 24.0));
            auto clip = new otio::Clip("Sequence", isr);
            track->append_child(clip);

            // Write the bundle.
            std::filesystem::path const temp_file = temp_dir / "test.otioz";
            bundle::WriteOptions        write_options;
            write_options.parent_path = temp_dir.u8string();
            assertTrue(bundle::to_otioz(
                timeline,
                temp_file.u8string(),
                write_options));
            
            // Extract the bundle.
            bundle::OtiozReadOptions    read_options;
            std::filesystem::path const output_path = temp_dir / "extract";
            read_options.extract_path = output_path.u8string();
            auto result = bundle::from_otioz(
                temp_file.u8string(),
                read_options);
            
            // Check the media exists.
            for (int frame = 0; frame < sequence_frames; ++frame)
            {
                std::stringstream ss;
                ss << name_prefix <<
                    std::setfill('0') << std::setw(frame_zero_padding) <<
                    frame <<
                    name_suffix;
                assertTrue(std::filesystem::exists(
                    output_path / bundle::media_dir / ss.str()));
            }
        });

    tests.run(argc, argv);
    return 0;
}
