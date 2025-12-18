// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @name File Utilities
///@{

/// @brief Convert Windows path separators to UNIX path separators.
OTIO_API std::string to_unix_separators(std::string const&);

/// @brief Create a temporary directory.
///
/// This function is only used for the tests and examples.
OTIO_API std::string create_temp_dir();

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
