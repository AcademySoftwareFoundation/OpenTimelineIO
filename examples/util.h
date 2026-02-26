// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <opentimelineio/errorStatus.h>

#include <vector>

namespace examples {

// Normalize path (change '\' path delimiters to '/').
std::string normalize_path(std::string const&);

// Get the absolute path.
std::string absolute(std::string const&);

// Create a temporary directory.
std::string create_temp_dir();

// Get a list of files from a directory.
std::vector<std::string> glob(std::string const& path, std::string const& pattern);

// Print an error to std::cerr.
void print_error(opentimelineio::OPENTIMELINEIO_VERSION_NS::ErrorStatus const&);

}
