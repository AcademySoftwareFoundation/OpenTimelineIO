#ifndef OTIO_DESERIALIZATIONH
#define OTIO_DESERIALIZATIONH

#include <string>
#include "any.hpp"
#include "serializableObject.h"

bool deserialize_json_from_string(std::string const& input, any* destination, std::string* err_msg);

bool deserialize_json_from_file(std::string const& file_name, any* destination, std::string* err_msg);

#endif
