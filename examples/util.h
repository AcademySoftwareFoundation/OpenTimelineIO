#pragma once

#include <opentimelineio/version.h>

#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

class ErrorStatus;
class Timeline;

} }

// This class provides file reading/writing using the Python file adapters.
class PythonAdapters
{
public:
    PythonAdapters();
    ~PythonAdapters();
    
    opentimelineio::OPENTIMELINEIO_VERSION::Timeline* read_from_file(
        std::string const&,
        opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus*);
    
    bool write_to_file(
        const opentimelineio::OPENTIMELINEIO_VERSION::Timeline*,
        std::string const&,
        opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus*);

private:
    void _convert(std::string const& in_file_name, std::string const& out_file_name);
};

// Print an error to std::cout.
void print_error(opentimelineio::OPENTIMELINEIO_VERSION::ErrorStatus const&);

