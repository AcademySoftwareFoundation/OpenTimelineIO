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
        //std::filesystem::current_path() / "sample_data";
        "C:/Dev/otio/darby/tests/sample_data";
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

    tests.run(argc, argv);
    return 0;
}
