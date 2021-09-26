#pragma once

#include <opentimelineio/errorStatus.h>

#include <vector>

namespace examples {

#if defined(_WINDOWS)
#define OTIO_EXAMPLES_MAIN() int wmain(int argc, wchar_t* argv[])
#else // _WINDOWS
#define OTIO_EXAMPLES_MAIN() int main(int argc, char* argv[])
#endif // _WINDOWS

// Get the list of command line arguments.
std::vector<std::string> args(int, char**);

// Get the list of command line arguments.
std::vector<std::string> args(int, wchar_t**);

// Normalize path (change '\' path delimeters to '/').
std::string normalize_path(std::string const&);

// Get the absolute path.
std::string absolute(std::string const&);

// Create a temporary directory.
std::string create_temp_dir();

// Get a list of files from a directory.
std::vector<std::string> glob(std::string const& path, std::string const& pattern);

// Print an error to std::cerr.
void print_error(opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus const&);

}

