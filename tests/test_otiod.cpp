// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/bundle.h>
#include <opentimelineio/bundleUtils.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/missingReference.h>

#include <iostream>

namespace otime  = opentime::OPENTIME_VERSION;
namespace otio   = opentimelineio::OPENTIMELINEIO_VERSION;
namespace bundle = opentimelineio::OPENTIMELINEIO_VERSION::bundle;

int
main(int argc, char** argv)
{
    Tests tests;

    // Sample data paths.
    std::filesystem::path const sample_data_dir =
        std::filesystem::current_path() / "sample_data";
    std::string const screening_example_path = bundle::to_unix_separators(
        (sample_data_dir / "screening_example.otio").u8string());

    // Sample media paths.
    std::string const media_example_path_rel     = "OpenTimelineIO@3xDark.png";
    std::string const media_example_path_url_rel = bundle::to_unix_separators(
        bundle::url_from_filepath(media_example_path_rel));
    std::string const media_example_path_abs = bundle::to_unix_separators(
        (sample_data_dir / "OpenTimelineIO@3xLight.png").u8string());
    std::string const media_example_path_url_abs = bundle::to_unix_separators(
        bundle::url_from_filepath(media_example_path_abs));

    // Test timeline.
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
        dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(
            screening_example_path)));
    
    // Convert to contrived local references.
    bool last_rel = false;
    for (auto cl : timeline->find_clips())
    {
        // Vary the relative and absolute paths, make sure that both work.
        std::string const next_rel = last_rel ? media_example_path_url_rel
                                              : media_example_path_url_abs;
        last_rel                   = !last_rel;
        cl->set_media_reference(new otio::ExternalReference(next_rel));
    }

    tests.add_test(
        "test_file_bundle_manifest_missing_reference",
        [sample_data_dir, timeline]
        {
            std::map<std::filesystem::path, std::filesystem::path> manifest;
            auto result_timeline = bundle::timeline_for_bundle_and_manifest(
                timeline,
                sample_data_dir,
                bundle::MediaReferencePolicy::AllMissing,
                manifest);

            // All missing should be empty.
            assertTrue(manifest.empty());
            for (auto cl : result_timeline->find_clips())
            {
                assertTrue(dynamic_cast<otio::MissingReference*>(cl->media_reference()));
            }
        });

    tests.add_test(
        "test_file_bundle_manifest",
        [sample_data_dir,
         media_example_path_abs,
         media_example_path_rel,
        timeline]
        {
            std::map<std::filesystem::path, std::filesystem::path> manifest;
            auto result_timeline = bundle::timeline_for_bundle_and_manifest(
                timeline,
                sample_data_dir,
                bundle::MediaReferencePolicy::ErrorIfNotFile,
                manifest);
            assertEqual(manifest.size(), 2);

            // Compare absolute paths.
            std::set<std::filesystem::path> const known_files = {
                std::filesystem::u8path(media_example_path_abs),
                sample_data_dir / std::filesystem::u8path(media_example_path_rel)
            };
            std::set<std::filesystem::path> manifest_abs;
            for (const auto& i : manifest)
            {
                manifest_abs.insert(i.first);
            }
            assertEqual(manifest_abs, known_files);
        });

    tests.add_test(
        "test_round_trip",
        [sample_data_dir, media_example_path_url_rel, timeline]
        {
            std::string const       temp_file = get_temp_file(".otiod");
            bundle::ToBundleOptions options;
            options.parent_path = sample_data_dir.u8string();
            assertTrue(bundle::to_otiod(timeline, temp_file, options));

            // By default will provide relative paths.
            auto result = bundle::from_otiod(temp_file);
            for (auto cl: result->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    assertTrue(std::filesystem::u8path(
                                   bundle::filepath_from_url(er->target_url()))
                                   .is_relative());
                }
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
                    std::filesystem::path const path =
                        bundle::filepath_from_url(er->target_url());
                    er->set_target_url(bundle::url_from_filepath(
                        (bundle::media_dir / path.filename()).u8string()));
                }
            }

            assertEqual(
                result->to_json_string(),
                clone->to_json_string());
        });

    tests.add_test(
        "test_round_trip_all_missing_references",
        [sample_data_dir, timeline]
        {
            std::string const       temp_file = get_temp_file(".otiod");
            bundle::ToBundleOptions options;
            options.parent_path = sample_data_dir.u8string();
            options.media_policy = bundle::MediaReferencePolicy::AllMissing;
            assertTrue(bundle::to_otiod(timeline, temp_file, options));

            auto result = bundle::from_otiod(temp_file);

            for (auto clip: result->find_clips())
            {
                assertTrue(dynamic_cast<otio::MissingReference*>(
                    clip->media_reference()));
            }
        });

    tests.add_test(
        "test_round_trip_absolute_paths",
        [sample_data_dir, media_example_path_url_rel, timeline]
        {
            std::string const       temp_file = get_temp_file(".otiod");
            bundle::ToBundleOptions to_options;
            to_options.parent_path = sample_data_dir.u8string();
            assertTrue(bundle::to_otiod(timeline, temp_file, to_options));

            // Can optionally generate absolute paths.
            bundle::FromOtiodOptions options;
            options.absolute_media_reference_paths = true;
            auto result = bundle::from_otiod(temp_file, options);

            for (auto clip: result->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    clip->media_reference()))
                {
                    assertTrue(std::filesystem::u8path(
                                   bundle::filepath_from_url(er->target_url()))
                                   .is_absolute());
                }
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
                    std::filesystem::path const path =
                        bundle::filepath_from_url(er->target_url());
                    er->set_target_url(bundle::url_from_filepath(
                        (std::filesystem::u8path(temp_file) / bundle::media_dir / path.filename()).u8string()));
                }
            }

            assertEqual(
                result->to_json_string(),
                clone->to_json_string());
        });

    tests.run(argc, argv);
    return 0;
}
