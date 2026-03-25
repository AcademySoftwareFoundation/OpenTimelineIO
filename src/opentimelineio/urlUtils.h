// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

#include <memory>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Interface for URL utilities.
class OTIO_API_TYPE IURLUtils : public std::enable_shared_from_this<IURLUtils>
{
public:
    OTIO_API virtual ~IURLUtils() = 0;

    /// @brief Get the scheme from a URL (i.e., "file" or "https").
    OTIO_API virtual std::string scheme_from_url(std::string const&) = 0;

    /// @brief Encode a URL (i.e., replace " " characters with "%20").
    OTIO_API virtual std::string url_encode(std::string const& url) = 0;

    /// @brief Decode a URL (i.e., replace "%20" strings with " ").
    OTIO_API virtual std::string url_decode(std::string const& url) = 0;

    /// @brief Convert a filesystem path to a file URL.
    ///
    /// For example:
    /// * "/var/tmp/thing.otio" -> "file:///var/tmp/thing.otio"
    /// * "subdir/thing.otio" -> "tmp/thing.otio"
    OTIO_API virtual std::string url_from_filepath(std::string const&) = 0;

    /// @brief Convert a file URL to a filesystem path.
    ///
    /// URLs can either be encoded according to the `RFC 3986` standard or not.
    /// Additionally, Windows mapped drive letter and UNC paths need to be
    /// accounted for when processing URLs.
    ///
    /// RFC 3986: https://tools.ietf.org/html/rfc3986
    OTIO_API virtual std::string filepath_from_url(std::string const&) = 0;
};

/// @brief Default URL utilities.
class OTIO_API_TYPE DefaultURLUtils : public IURLUtils
{
public:
    OTIO_API std::string scheme_from_url(std::string const&) override;
    OTIO_API std::string url_encode(std::string const& url) override;
    OTIO_API std::string url_decode(std::string const& url) override;
    OTIO_API std::string url_from_filepath(std::string const&) override;
    OTIO_API std::string filepath_from_url(std::string const&) override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
