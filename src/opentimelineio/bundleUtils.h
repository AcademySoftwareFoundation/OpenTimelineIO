// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/bundle.h"

#include <filesystem>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

/// @brief Convert a media reference policy to a string.
std::string to_string(MediaReferencePolicy);

/// @brief Convert Windows path separators to UNIX path separators.
std::string to_unix_separators(std::string const&);

/// @brief Get the scheme from a URL.
std::string scheme_from_url(std::string const&);

/// @brief Encode a URL (i.e., replace " " characters with "%20").
std::string url_encode(std::string const& url);

/// @brief Decode a URL (i.e., replace "%20" strings with " ").
std::string url_decode(std::string const& url);

/// @brief Convert a filesystem path to a file URL.
///
/// For example:
/// * "/var/tmp/thing.otio" -> "file:///var/tmp/thing.otio"
/// * "subdir/thing.otio" -> "tmp/thing.otio"
///
/// @todo Hopefully this can be replaced by functionality from the C++
/// standard library at some point.
std::string url_from_filepath(std::string const&);

/// @brief Convert a file URL to a filesystem path.
///
/// URLs can either be encoded according to the `RFC 3986` standard or not.
/// Additionally, Windows mapped drive letter and UNC paths need to be
/// accounted for when processing URLs.
///
/// RFC 3986: https://tools.ietf.org/html/rfc3986
///
/// @todo Hopefully this can be replaced by functionality from the C++
/// standard library at some point.
std::string filepath_from_url(std::string const&);

/// @brief This maps absolute paths of media references to their relative
/// paths in the bundle media directory.
typedef std::map<std::filesystem::path, std::filesystem::path> Manifest;

/// @brief Create a new timeline based on the input timeline that has media
/// references replaced according to the media reference policy.
///
/// The media references are relinked to relative file paths in the media
/// directory.
///
/// This is considered an internal API.
/// 
/// Throws std::exception on errors.
SerializableObject::Retainer<Timeline> timeline_for_bundle_and_manifest(
    SerializableObject::Retainer<Timeline> const&,
    std::filesystem::path const& timeline_dir,
    MediaReferencePolicy media_reference_policy,
    Manifest& output_manifest);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
