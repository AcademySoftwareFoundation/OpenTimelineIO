// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/typeRegistry.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Timeline;

namespace bundle {

/// @brief This constant provides the current otioz version.
static std::string const otiozVersion = "1.0.0";

/// @brief This constant provides the current otiod version.
static std::string const otiodVersion = "1.0.0";

/// @brief This enumeration provides the bundle media reference policy.
enum class BundleMediaReferencePolicy
{
    ErrorIfNotFile,
    MissingIfNotFile,
    AllMissing
};

/// @brief Convert Windows path separators to UNIX path separators.
std::string to_unix_separators(const std::string&);

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

/// @brief Write a timeline and it's referenced media to an .otiod bundle.
///
/// @param timeline The timeline to write.
/// @param file_name The bundle file name.
/// @param media_reference_policy The media reference policy.
/// @param error_status The return status.
/// @param target_family_label_spec @todo Add comment.
/// @param indent The number of spaces to use for indentation.
bool to_otiod_bundle(
    Timeline const*            timeline,
    std::string const&         file_name,
    BundleMediaReferencePolicy media_reference_policy =
        BundleMediaReferencePolicy::ErrorIfNotFile,
    ErrorStatus*              error_status             = nullptr,
    const schema_version_map* target_family_label_spec = nullptr,
    int                       indent                   = 4);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
