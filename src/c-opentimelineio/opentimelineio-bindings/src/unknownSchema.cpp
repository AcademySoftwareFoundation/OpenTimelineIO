#include "copentimelineio/unknownSchema.h"
#include <opentimelineio/unknownSchema.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    UnknownSchema* UnknownSchema_create(
        const char* original_schema_name, int original_schema_version)
    {
        return reinterpret_cast<UnknownSchema*>(new OTIO_NS::UnknownSchema(
            original_schema_name, original_schema_version));
    }
    const char* UnknownSchema_original_schema_name(UnknownSchema* self)
    {
        std::string returnStr = reinterpret_cast<OTIO_NS::UnknownSchema*>(self)
                                    ->original_schema_name();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    int UnknownSchema_original_schema_version(UnknownSchema* self)
    {
        return reinterpret_cast<OTIO_NS::UnknownSchema*>(self)
            ->original_schema_version();
    }
    _Bool UnknownSchema_is_unknown_schema(UnknownSchema* self)
    {
        return reinterpret_cast<OTIO_NS::UnknownSchema*>(self)
            ->is_unknown_schema();
    }
#ifdef __cplusplus
}
#endif
