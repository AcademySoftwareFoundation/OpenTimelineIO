// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @name URL Utilities
/// @todo Should we use a third party library for handling URLs?
///@{

/// @brief Get the scheme from a URL.
OTIO_API std::string scheme_from_url(std::string const&);

/// @brief Encode a URL (i.e., replace " " characters with "%20").
OTIO_API std::string url_encode(std::string const& url);

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
OTIO_API std::string url_from_filepath(std::string const&);

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
OTIO_API std::string filepath_from_url(std::string const&);

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
