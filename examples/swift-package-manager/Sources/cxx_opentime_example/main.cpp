#include <iostream>
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"

namespace ot = opentime::OPENTIME_VERSION;

int main() {
    auto rt = ot::RationalTime(3, 24);
    auto tr = ot::TimeRange(rt, ot::RationalTime(48, 24));
    std::cout << rt.to_time_string() << "\n";
    std::cout << "start time: " << tr.start_time().to_time_string() <<
                 ", duration: " << tr.duration().to_time_string() << "\n";
}

