// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include "opentimelineio/bundle.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/fileUtils.h"
#include "opentimelineio/imageSequenceReference.h"
#include "opentimelineio/missingReference.h"
#include "opentimelineio/urlUtil.h"

#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>

using namespace OTIO_NS;
using namespace OTIO_NS::bundle;

int
main(int argc, char** argv)
{
    Tests tests;

    auto url_util = std::make_shared<DefaultURLUtil>();

    // Sample data paths.
    std::filesystem::path const sample_data_dir =
        std::filesystem::u8path(OTIO_TESTS_DIR) / "sample_data";
    std::string const screening_example_path = to_unix_separators(
        (sample_data_dir / "screening_example.otio").u8string());

    // Sample media paths.
    std::string const media_example_path_rel     = "OpenTimelineIO@3xDark.png";
    std::string const media_example_path_url_rel = to_unix_separators(
        url_util->url_from_filepath(media_example_path_rel));
    std::string const media_example_path_abs = to_unix_separators(
        (sample_data_dir / "OpenTimelineIO@3xLight.png").u8string());
    std::string const media_example_path_url_abs = to_unix_separators(
        url_util->url_from_filepath(media_example_path_abs));

    // Test timeline.
    SerializableObject::Retainer<Timeline> timeline(
        dynamic_cast<Timeline*>(Timeline::from_json_file(
            screening_example_path)));
    
    // Convert to contrived local references.
    bool last_rel = false;
    for (auto cl : timeline->find_clips())
    {
        // Vary the relative and absolute paths, make sure that both work.
        std::string const next_rel = last_rel ? media_example_path_url_rel
                                              : media_example_path_url_abs;
        last_rel                   = !last_rel;
        cl->set_media_reference(new ExternalReference(next_rel));
    }

    tests.add_test(
        "test_round_trip",
        [url_util, sample_data_dir, media_example_path_url_rel, timeline]
        {
            std::filesystem::path const temp_dir  = create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otiod";
            WriteOptions write_options;
            write_options.parent_path = sample_data_dir.u8string();
            write_options.url_util = url_util;
            assertTrue(to_otiod(timeline, temp_file.u8string(), write_options));

            // By default will provide relative paths.
            OtiodReadOptions read_options;
            read_options.url_util = url_util;
            auto result = from_otiod(temp_file.u8string(), read_options);
            for (auto cl: result->find_clips())
            {
                if (auto er = dynamic_cast<ExternalReference*>(
                    cl->media_reference()))
                {
                    assertTrue(std::filesystem::u8path(
                                   url_util->filepath_from_url(er->target_url()))
                                   .is_relative());
                }
            }

            // Clone the input and conform the media references to what they
            // should be in the output.
            SerializableObject::Retainer<Timeline> clone(
                dynamic_cast<Timeline*>(timeline->clone()));
            for (auto cl: clone->find_clips())
            {
                if (auto er = dynamic_cast<ExternalReference*>(
                    cl->media_reference()))
                {
                    std::filesystem::path const path =
                        url_util->filepath_from_url(er->target_url());
                    er->set_target_url(url_util->url_from_filepath(
                        (media_dir / path.filename()).u8string()));
                }
            }

            assertEqual(
                result->to_json_string(),
                clone->to_json_string());
        });

    tests.add_test(
        "test_round_trip_all_missing_references",
        [url_util, sample_data_dir, timeline]
        {
            std::filesystem::path const temp_dir  = create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otiod";
            WriteOptions write_options;
            write_options.parent_path = sample_data_dir.u8string();
            write_options.media_policy = MediaReferencePolicy::AllMissing;
            write_options.url_util = url_util;
            assertTrue(to_otiod(
                timeline,
                temp_file.u8string(),
                write_options));

            OtiodReadOptions read_options;
            read_options.url_util = url_util;
            auto result = from_otiod(temp_file.u8string(), read_options);

            for (auto clip: result->find_clips())
            {
                assertTrue(dynamic_cast<MissingReference*>(
                    clip->media_reference()));
            }
        });

    tests.add_test(
        "test_round_trip_absolute_paths",
        [url_util, sample_data_dir, media_example_path_url_rel, timeline]
        {
            std::filesystem::path const temp_dir  = create_temp_dir();
            std::filesystem::path const temp_file = temp_dir / "test.otiod";
            WriteOptions write_options;
            write_options.parent_path = sample_data_dir.u8string();
            write_options.url_util = url_util;
            assertTrue(to_otiod(
                timeline,
                temp_file.u8string(),
                write_options));

            // Can optionally generate absolute paths.
            OtiodReadOptions read_options;
            read_options.absolute_media_reference_paths = true;
            read_options.url_util = url_util;
            auto result = from_otiod(temp_file.u8string(), read_options);

            for (auto clip: result->find_clips())
            {
                if (auto er = dynamic_cast<ExternalReference*>(
                    clip->media_reference()))
                {
                    assertTrue(std::filesystem::u8path(
                                   url_util->filepath_from_url(er->target_url()))
                                   .is_absolute());
                }
            }

            // Clone the input and conform the media references to what they
            // should be in the output.
            SerializableObject::Retainer<Timeline> clone(
                dynamic_cast<Timeline*>(timeline->clone()));
            for (auto cl: clone->find_clips())
            {
                if (auto er = dynamic_cast<ExternalReference*>(
                        cl->media_reference()))
                {
                    std::filesystem::path const path =
                        url_util->filepath_from_url(er->target_url());
                    er->set_target_url(url_util->url_from_filepath(
                        (temp_file / media_dir / path.filename()).u8string()));
                }
            }

            assertEqual(
                result->to_json_string(),
                clone->to_json_string());
        });

    tests.add_test(
        "test_round_trip_with_sequence",
        [url_util, sample_data_dir, media_example_path_rel]
        {
            // Create an image sequence.
            std::filesystem::path const temp_dir = create_temp_dir();
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
            SerializableObject::Retainer<Timeline> timeline(new Timeline);
            auto track = new Track;
            timeline->tracks()->append_child(track);
            auto isr = new ImageSequenceReference(
                "",
                name_prefix,
                name_suffix,
                0,
                1,
                24.0,
                frame_zero_padding,
                ImageSequenceReference::MissingFramePolicy::error,
                TimeRange(0.0, sequence_frames, 24.0));
            auto clip = new Clip("Sequence", isr);
            track->append_child(clip);

            // Write the bundle.
            std::filesystem::path const temp_file = temp_dir / "test.otiod";
            WriteOptions                write_options;
            write_options.parent_path = temp_dir.u8string();
            write_options.url_util = url_util;
            assertTrue(to_otiod(
                timeline,
                temp_file.u8string(),
                write_options));

            // Check the media exists.
            for (int frame = 0; frame < sequence_frames; ++frame)
            {
                std::stringstream ss;
                ss << name_prefix <<
                    std::setfill('0') << std::setw(frame_zero_padding) <<
                    frame <<
                    name_suffix;
                assertTrue(std::filesystem::exists(
                    temp_file / media_dir / ss.str()));
            }
        });

    tests.run(argc, argv);
    return 0;
}
