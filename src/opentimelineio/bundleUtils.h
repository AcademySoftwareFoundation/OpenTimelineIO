// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

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

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
