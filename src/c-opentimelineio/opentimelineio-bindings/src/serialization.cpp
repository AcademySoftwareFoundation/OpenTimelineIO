#include "copentimelineio/serialization.h"
#include <opentimelineio/serialization.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    const char* serialize_json_to_string(
        Any* value, OTIOErrorStatus* error_status, int indent)
    {
        std::string returnStr = OTIO_NS::serialize_json_to_string(
            *reinterpret_cast<OTIO_NS::any*>(value),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status),
            indent);
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    _Bool serialize_json_to_file(
        Any*             value,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return OTIO_NS::serialize_json_to_file(
            reinterpret_cast<OTIO_NS::any*>(value),
            file_name,
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status),
            indent);
    }
#ifdef __cplusplus
}
#endif