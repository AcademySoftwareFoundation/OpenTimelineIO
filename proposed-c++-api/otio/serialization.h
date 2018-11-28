#ifndef OTIO_SERIALIZATION_H
#define OTIO_SERIALIZATION_H

#include <string>
#include "any.hpp"

std::string serialize_json_to_string(const any& value, std::string* errMsg, int indent = 4);

bool serialize_json_to_file(std::string const& file_name,
                            const any& value, std::string* errMsg, int indent = 4);

#endif
