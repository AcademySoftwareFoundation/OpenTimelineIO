#include <cstdlib>
#include <memory>
#include <cxxabi.h>
#include <string>
#include "opentimelineio/serializableObject.h"

std::string demangled_type_name(const char* name) {
    int status = -4; // some arbitrary value to eliminate the compiler warning

    std::unique_ptr<char, void(*)(void*)> res {
        abi::__cxa_demangle(name, NULL, NULL, &status),
            std::free
            };

    return (status==0) ? res.get() : name;
}

std::string demangled_type_name(std::type_info const& t) {
    if (t == typeid(std::string)) {
        return "string";
    }
    if (t == typeid(void)) {
        return "None";
    }
    
    return demangled_type_name(t.name());
}

std::string demangled_type_name(any const& a) {
    return demangled_type_name(a.type());
}

std::string demangled_type_name(SerializableObject* so) {
    return demangled_type_name(typeid(*so));
}

std::string demangled_type_name(class SerializableObject*);

void fatal_error(std::string const& errMsg) {
    fprintf(stderr, "Fatal error: %s\n", errMsg.c_str());
    exit(-1);
}

bool split_schema_string(std::string const& schema_and_version, std::string* schema_name, int* schema_version) {
    size_t index = schema_and_version.rfind('.');
    if (index == std::string::npos) {
        return false;
    }

    *schema_name = schema_and_version.substr(0, index);
    try {
        *schema_version = std::stoi(schema_and_version.substr(index+1));
        return true;
    } catch (...) {
        return false;
    }
}
