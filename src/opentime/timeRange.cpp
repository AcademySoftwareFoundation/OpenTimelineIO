#include "opentime/timeRange.h"
#include "opentime/stringPrintf.h"

namespace opentime {
    
std::string TimeRange::description() const {
    return string_printf("TimeRange(%s, %s)",
                        _start_time.description().c_str(), _duration.description().c_str());
}

}
