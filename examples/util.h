#pragma once

#include <opentimelineio/errorStatus.h>

#include <vector>

// Normalize path (change '\' path delimeters to '/').
std::string normalize_path(std::string const&);

// Create a temporary directory.
std::string create_temp_dir();

// Get a list of files from a directory.
std::vector<std::string> glob(std::string const&);

// Print an error to std::cerr.
void print_error(opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus const&);

