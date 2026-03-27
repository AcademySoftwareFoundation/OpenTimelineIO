// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/fileUtils.h>
#include <opentimelineio/urlUtils.h>

#include <filesystem>
#include <iostream>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    auto url_utils = std::make_shared<DefaultURLUtils>();

    // Sample data paths.
    std::filesystem::path const sample_data_dir =
        std::filesystem::u8path(OTIO_TESTS_DIR) / "sample_data";
    std::string const screening_example_path = to_unix_separators(
        (sample_data_dir / "screening_example.otio").u8string());

    // Sample media paths.
    std::string const media_example_path_rel = "OpenTimelineIO@3xDark.png";
    std::string const media_example_path_url_rel = to_unix_separators(
        url_utils->url_from_filepath(media_example_path_rel));
    std::string const media_example_path_abs = to_unix_separators(
        (sample_data_dir / "OpenTimelineIO@3xLight.png").u8string());
    std::string const media_example_path_url_abs = to_unix_separators(
        url_utils->url_from_filepath(media_example_path_abs));

    // Windows test paths.
    std::string const windows_encoded_url = "file://host/S%3a/path/file.ext";
    std::string const windows_drive_url   = "file://S:/path/file.ext";
    std::string const windows_drive_path  = "S:/path/file.ext";

    // Windows UNC test paths.
    std::string const windows_encoded_unc_url =
        "file://unc/path/sub%20dir/file.ext";
    std::string const windows_unc_url  = "file://unc/path/sub dir/file.ext";
    std::string const windows_unc_path = "//unc/path/sub dir/file.ext";

    // POSIX test paths.
    std::string const posix_localhost_url =
        "file://localhost/path/sub dir/file.ext";
    std::string const posix_encoded_url = "file:///path/sub%20dir/file.ext";
    std::string const posix_url         = "file:///path/sub dir/file.ext";
    std::string const posix_path        = "/path/sub dir/file.ext";

    tests.add_test(
        "test_roundtrip_abs",
        [url_utils, media_example_path_abs, media_example_path_url_abs] {
            assertEqual(media_example_path_url_abs.substr(0, 7), std::string("file://"));
            std::string const filepath =
                url_utils->filepath_from_url(media_example_path_url_abs);
            assertEqual(filepath, media_example_path_abs);
        });

    tests.add_test(
        "test_roundtrip_rel",
        [url_utils, media_example_path_rel, media_example_path_url_rel] {
            assertNotEqual(media_example_path_url_rel.substr(0, 7), std::string("file://"));
            std::string const filepath =
                url_utils->filepath_from_url(media_example_path_url_rel);
            assertEqual(filepath, media_example_path_rel);
        });

    tests.add_test(
        "test_windows_urls",
        [url_utils, windows_encoded_url, windows_drive_url, windows_drive_path] {
            for (auto const url : { windows_encoded_url, windows_drive_url }) {
                std::string const filepath = url_utils->filepath_from_url(url);
                assertEqual(filepath, windows_drive_path);
            }
        });

    tests.add_test(
        "test_windows_unc_urls",
        [url_utils, windows_encoded_unc_url, windows_unc_url, windows_unc_path] {
            for (auto const url : { windows_encoded_unc_url, windows_unc_url }) {
                std::string const filepath = url_utils->filepath_from_url(url);
                assertEqual(filepath, windows_unc_path);
            }
        });

    tests.add_test(
        "test_posix_urls",
        [url_utils, posix_encoded_url, posix_url, posix_localhost_url, posix_path] {
            for (auto const url : { posix_encoded_url, posix_url }) {
                std::string const filepath = url_utils->filepath_from_url(url);
                assertEqual(filepath, posix_path);
            }
        });

    tests.add_test(
        "test_relative_url",
        [url_utils] {
            // See github issue #1817 - when a relative URL has only one name after
            // the "." (ie ./blah but not ./blah/blah)
            std::string const filepath = url_utils->filepath_from_url(
                (std::filesystem::path(".") / std::filesystem::path("docs")).u8string());
            assertEqual(filepath, std::string("docs"));
        });

    tests.run(argc, argv);
    return 0;
}
