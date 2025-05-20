// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/bundle.h>

#include <filesystem>
#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;

    const std::filesystem::path sample_data_dir = std::filesystem::current_path() / "sample_data";
    const std::string screening_example_path = (sample_data_dir / "screening_example.otio").u8string();
    const std::string media_example_path_rel = "OpenTimelineIO@3xDark.png";
    const std::string media_example_path_url_rel = otio::url_from_filepath(media_example_path_rel);
    const std::string media_example_path_abs = (sample_data_dir / "OpenTimelineIO@3xLight.png").u8string();
    const std::string media_example_path_url_abs = otio::url_from_filepath(media_example_path_abs);

    const std::string windows_encoded_url = "file://host/S%3a/path/file.ext";
    const std::string windows_drive_url = "file://S:/path/file.ext";
    const std::string windows_drive_path = "S:/path/file.ext";

    const std::string windows_encoded_unc_url = "file://unc/path/sub%20dir/file.ext";
    const std::string windows_unc_url = "file://unc/path/sub dir/file.ext";
    const std::string windows_unc_path = "//unc/path/sub dir/file.ext";

    const std::string posix_localhost_url = "file://localhost/path/sub dir/file.ext";
    const std::string posix_encoded_url = "file:///path/sub%20dir/file.ext";
    const std::string posix_url = "file:///path/sub dir/file.ext";
    const std::string posix_path = "/path/sub dir/file.ext";

    tests.add_test(
        "test_roundtrip_abs",
        [media_example_path_abs, media_example_path_url_abs] {
            assertEqual(media_example_path_url_abs.substr(0, 7), std::string("file://"));
            const std::string filepath = otio::filepath_from_url(media_example_path_url_abs);
            assertEqual(filepath, media_example_path_abs);
        });

    tests.add_test(
        "test_roundtrip_rel",
        [media_example_path_rel, media_example_path_url_rel] {
            assertNotEqual(media_example_path_url_rel.substr(0, 7), std::string("file://"));
            const std::string filepath = otio::filepath_from_url(media_example_path_url_rel);
            assertEqual(filepath, media_example_path_rel);
        });

    tests.add_test(
        "test_windows_urls",
        [windows_encoded_url, windows_drive_url, windows_drive_path] {
            for (const auto url : { windows_encoded_url, windows_drive_url }) {
                const std::string filepath = otio::filepath_from_url(url);
                assertEqual(filepath, windows_drive_path);
            }
        });

    tests.add_test(
        "test_windows_unc_urls",
        [windows_encoded_unc_url, windows_unc_url, windows_unc_path] {
            for (const auto url : { windows_encoded_unc_url, windows_unc_url }) {
                const std::string filepath = otio::filepath_from_url(url);
                assertEqual(filepath, windows_unc_path);
            }
        });

    tests.add_test(
        "test_posix_urls",
        [posix_encoded_url, posix_url, posix_localhost_url, posix_path] {
            for (const auto url : { posix_encoded_url, posix_url }) {
                const std::string filepath = otio::filepath_from_url(url);
                assertEqual(filepath, posix_path);
            }
        });

    tests.add_test(
        "test_relative_url",
        [] {
            // See github issue #1817 - when a relative URL has only one name after
            // the "." (ie ./blah but not ./blah/blah)
            const std::string filepath = otio::filepath_from_url(
                std::filesystem::path(".") / std::filesystem::path("docs"));
            assertEqual(filepath, std::string("docs"));
        });

    tests.run(argc, argv);
    return 0;
}
