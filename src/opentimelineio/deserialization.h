#ifndef OTIO_DESERIALIZATIONH
#define OTIO_DESERIALIZATIONH

#include <string>
#include "opentimelineio/any.h"
#include "opentimelineio/serializableObject.h"

bool deserialize_json_from_string(std::string const& input, any* destination, ErrorStatus* error_status); 

bool deserialize_json_from_file(std::string const& file_name, any* destination, ErrorStatus* error_status);

#endif
