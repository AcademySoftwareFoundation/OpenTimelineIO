#include <iostream>

#include "util.h"
#include <opentimelineio/any.h>
#include <opentimelineio/serialization.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/timeline.h>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

using chrono_time_point = std::chrono::steady_clock::time_point;

const void
print_elapsed_time(
        const std::string& message,
        const chrono_time_point& begin,
        const chrono_time_point& end
)
{
    const auto dur = (
            std::chrono::duration_cast<std::chrono::microseconds>(
                end - begin
            ).count()
    );
    std::cout << message << ": " << dur/1000000.0 << " [s]" << std::endl;
}

int
main(int argc, char *argv[])
{
    if (argc < 2) {
        std::cerr << "usage: otio_io_perf_test path/to/timeline.otio";
        std::cerr << std::endl;
        return 1;
    }

    otio::ErrorStatus err;
    otio::any tl;
    std::string fname = std::string(argv[1]);

    chrono_time_point begin = std::chrono::steady_clock::now();
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
            dynamic_cast<otio::Timeline*>(
                otio::Timeline::from_json_file(argv[1], &err)
            )
    );
    chrono_time_point end = std::chrono::steady_clock::now();
    if (!timeline)
    {
        examples::print_error(err);
        return 1;
    }

    print_elapsed_time("deserialize_json_from_file", begin, end);

    begin = std::chrono::steady_clock::now();
    const std::string result = timeline.value->to_json_string(&err);
    if (otio::is_error(err))
    {
        examples::print_error(err);
        return 1;
    }
    end = std::chrono::steady_clock::now();
    print_elapsed_time("serialize_json_to_string", begin, end);

    return 0;
}
