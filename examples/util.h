#pragma once

#include <opentimelineio/serializableObject.h>

#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

struct ErrorStatus;
class Timeline;

} }

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

// This class provides file reading/writing using the Python file adapters.
class PythonAdapters
{
public:
    PythonAdapters();
    ~PythonAdapters();
    
    otio::SerializableObject::Retainer<otio::Timeline> read_from_file(
        std::string const&,
        otio::ErrorStatus*);
    
    bool write_to_file(
        otio::SerializableObject::Retainer<otio::Timeline> const&,
        std::string const&,
        otio::ErrorStatus*);

private:
    bool _convert(std::string const& in_file_name, std::string const& out_file_name);
};

// Print an error to std::cout.
void print_error(otio::ErrorStatus const&);

