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

    std::filesystem::path const sample_data_dir =
        std::filesystem::current_path() / "sample_data";
    std::string const screening_example_path = bundle::to_unix_separators(
        (sample_data_dir / "screening_example.otio").u8string());

    std::string const media_example_path_rel     = "OpenTimelineIO@3xDark.png";
    std::string const media_example_path_url_rel = bundle::to_unix_separators(
        bundle::url_from_filepath(media_example_path_rel));
    std::string const media_example_path_abs = bundle::to_unix_separators(
        (sample_data_dir / "OpenTimelineIO@3xLight.png").u8string());
    std::string const media_example_path_url_abs = bundle::to_unix_separators(
        bundle::url_from_filepath(media_example_path_abs));

    otio::SerializableObject::Retainer<otio::Timeline> timeline(
        dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(
            screening_example_path)));
    
    // Convert to contrived local reference.
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
            // All missing should be empty.
            std::map<std::filesystem::path, std::filesystem::path> manifest;
            auto result_timeline = bundle::timeline_for_bundle_and_manifest(
                timeline,
                sample_data_dir,
                bundle::MediaReferencePolicy::AllMissing,
                manifest);
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

            std::set<std::filesystem::path> known_files = {
                std::filesystem::u8path(media_example_path_abs),
                sample_data_dir / std::filesystem::u8path(media_example_path_rel)
            };
            std::set<std::filesystem::path> manifest_abs;
            for (const auto& i : manifest)
            {
                manifest_abs.insert(i.first);
            }

            // Should only contain absolute paths.
            assertEqual(manifest_abs, known_files);
        });

    tests.add_test(
        "test_round_trip",
        [sample_data_dir, media_example_path_url_rel, timeline]
        {
            std::string const temp_file =
                std::string(std::tmpnam(nullptr)) + ".otiod";
            assertTrue(bundle::to_otiod(
                timeline,
                sample_data_dir.u8string(),
                temp_file));

            // By default will provide relative paths.
            auto result = bundle::from_otiod(temp_file);

            for (auto cl: result.first->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    cl->media_reference()))
                {
                    assertNotEqual(
                        er->target_url(),
                        media_example_path_url_rel);
                }
            }

            // Conform media references in input to what they should be in the
            // output.
            for (auto cl: timeline->find_clips())
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
                result.first->to_json_string(),
                timeline->to_json_string());
        });

    tests.add_test(
        "test_round_trip_all_missing_references",
        [sample_data_dir, timeline]
        {
            std::string const temp_file =
                std::string(std::tmpnam(nullptr)) + ".otiod";
            bundle::ToBundleOptions toOptions;
            toOptions.media_reference_policy =
                bundle::MediaReferencePolicy::AllMissing;
            assertTrue(bundle::to_otiod(
                timeline,
                sample_data_dir.u8string(),
                temp_file,
                toOptions));

            auto result = bundle::from_otiod(temp_file);

            for (auto clip: result.first->find_clips())
            {
                assertTrue(dynamic_cast<otio::MissingReference*>(
                    clip->media_reference()));
            }
        });

    tests.add_test(
        "test_round_trip_absolute_paths",
        [sample_data_dir, media_example_path_url_rel, timeline]
        {
            // Reset the timeline URLs.
            for (auto clip: timeline->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    clip->media_reference()))
                {
                    std::filesystem::path const path = std::filesystem::u8path(
                        bundle::filepath_from_url(er->target_url()));
                    std::string const url =
                        bundle::url_from_filepath(path.filename().u8string());
                    er->set_target_url(url);
                }
            }

            std::string const temp_file =
                std::string(std::tmpnam(nullptr)) + ".otiod";
            assertTrue(bundle::to_otiod(
                timeline,
                sample_data_dir.u8string(),
                temp_file));

            // Can optionally generate absolute paths.
            bundle::FromOtiodOptions options;
            options.absolute_media_reference_paths = true;
            auto result = bundle::from_otiod(temp_file, options);

            for (auto clip: result.first->find_clips())
            {
                if (auto er = dynamic_cast<otio::ExternalReference*>(
                    clip->media_reference()))
                {
                    assertNotEqual(
                        er->target_url(),
                        media_example_path_url_rel);
                }
            }

            // Conform media references in input to what they should be in the
            // output.
            for (auto cl: timeline->find_clips())
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
                result.first->to_json_string(),
                timeline->to_json_string());
        });

    tests.run(argc, argv);
    return 0;
}
