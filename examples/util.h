// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <opentimelineio/errorStatus.h>

#include <vector>

namespace examples {

// Get the absolute path.
std::string absolute(std::string const&);

// Get a list of files from a directory.
std::vector<std::string> glob(std::string const& path, std::string const& pattern);

// Print an error to std::cerr.
void print_error(opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus const&);

}
