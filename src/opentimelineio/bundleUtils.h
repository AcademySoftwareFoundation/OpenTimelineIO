// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/bundle.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

/// @brief Version file name.
std::string const version_file = "version.txt";

/// @brief OTIO file name.
std::string const otio_file = "content.otio";

/// @brief Media directory name.
std::string const media_dir = "media";

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

/// @brief Create a new timeline based on input_otio that has had media
/// references replaced according to the media_policy.
/// 
/// Return that new timeline and a mapping of all the absolute file
/// paths (not URLs) to be used in the bundle, mapped to MediaReferences
/// associated with those files.
/// 
/// Media references in the timeline will be relinked by the adapters to point
/// to their output locations.
///
/// This is considered an internal API.
SerializableObject::Retainer<Timeline> timeline_for_bundle_and_manifest(
    SerializableObject::Retainer<Timeline> const&,
    std::string const&   timeline_dir,
    MediaReferencePolicy media_reference_policy,
    std::map<std::string, std::vector<SerializableObject::Retainer<ExternalReference>>>&,
    ErrorStatus& error_status);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
