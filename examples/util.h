#pragma once

#include <string>

// Create a unique temporary directory.
std::string get_temp_dir();

// Use Python to convert an input file to JSON. This is necessary
// because the OTIO adapters are not available from C++ yet.
void convert_to_json(std::string const& inFileName, std::string const& outFileName);

