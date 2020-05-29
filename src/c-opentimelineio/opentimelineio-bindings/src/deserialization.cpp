#include "copentimelineio/deserialization.h"
#include <opentimelineio/deserialization.h>

#ifdef __cplusplus
extern "C"
{
#endif
    _Bool deserialize_json_from_string(
        const char* input, Any* destination, OTIOErrorStatus* error_status)
    {
        std::string str = input;
        return OTIO_NS::deserialize_json_from_string(
            str,
            reinterpret_cast<OTIO_NS::any*>(destination),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool deserialize_json_from_file(
        const char* file_name, Any* destination, OTIOErrorStatus* error_status)
    {
        return OTIO_NS::deserialize_json_from_file(
            file_name,
            reinterpret_cast<OTIO_NS::any*>(destination),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
#ifdef __cplusplus
}
#endif