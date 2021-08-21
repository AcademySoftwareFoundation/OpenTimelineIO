#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/any.h"
#include "opentimelineio/serializableObject.h"

#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
bool deserialize_json_from_string(std::string const& input, any* destination, ErrorStatus* error_status); 

bool deserialize_json_from_file(std::string const& file_name, any* destination, ErrorStatus* error_status);
    
} }
