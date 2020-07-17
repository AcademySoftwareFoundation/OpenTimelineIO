#include "opentimelineio/serializableObject.h"
#if defined(__GNUC__) || defined(__clang__)
#include <cstdlib>
#include <memory>
#include <cxxabi.h>
#else
#include <typeinfo>
#endif

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
#if defined(__GNUC__) || defined(__clang__)
std::string cxxabi_demangled_type_name(const char* name) {
    int status = -4; // some arbitrary value to eliminate the compiler warning

    std::unique_ptr<char, void(*)(void*)> res {
        abi::__cxa_demangle(name, NULL, NULL, &status),
            std::free
            };

    return (status==0) ? res.get() : name;
}
#endif

std::string demangled_type_name(std::type_info const& t) {
    if (t == typeid(std::string)) {
        return "string";
    }
    if (t == typeid(void)) {
        return "None";
    }

#if defined(__GNUC__) || defined(__clang__)
    return cxxabi_demangled_type_name(t.name());
#else
    // On Windows std::type_info.name() returns a human readable string.
    return t.name();
#endif
}

std::string demangled_type_name(any const& a) {
    return demangled_type_name(a.type());
}

std::string demangled_type_name(SerializableObject* so) {
    return demangled_type_name(typeid(*so));
}

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

} }
