#pragma once

#include "opentime/version.h"
#include <string>
#include <cstdio>
#include <memory>

namespace opentime { namespace OPENTIME_VERSION {
    
template<typename ... Args>
std::string string_printf(char const* format, Args ... args )
{
    char buffer[4096];
    size_t size = snprintf(buffer, sizeof(buffer), format, args ... ) + 1;
    if (size < sizeof(buffer)) {
        return std::string(buffer);
    }
    
    std::unique_ptr<char[]> buf(new char[size]);
    std::snprintf(buf.get(), size, format, args ...);
    return std::string(buf.get());
}

} }
