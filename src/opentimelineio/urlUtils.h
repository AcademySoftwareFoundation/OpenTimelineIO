// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @name URL Utilities
///@{

/// @brief Get the scheme from a URL.
OTIO_API std::string scheme_from_url(std::string const&);

/// @brief Convert a filesystem path to a file URL.
OTIO_API std::string url_from_filepath(std::string const&);

/// @brief Convert a file URL to a filesystem path.
OTIO_API std::string filepath_from_url(std::string const&);

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
