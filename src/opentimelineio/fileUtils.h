// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @name File Utilities
///@{

/// @brief Convert Windows path separators to UNIX path separators.
std::string to_unix_separators(std::string const&);

// Create a temporary directory.
std::string create_temp_dir();

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
