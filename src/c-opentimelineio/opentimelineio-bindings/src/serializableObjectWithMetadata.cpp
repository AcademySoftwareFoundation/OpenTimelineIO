#include "copentimelineio/serializableObjectWithMetadata.h"
#include <opentimelineio/serializableObjectWithMetadata.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    SerializableObjectWithMetadata* SerializableObjectWithMetadata_create(
        const char* name, AnyDictionary* metadata)
    {
        return reinterpret_cast<SerializableObjectWithMetadata*>(
            new OTIO_NS::SerializableObjectWithMetadata(
                name, *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    const char*
    SerializableObjectWithMetadata_name(SerializableObjectWithMetadata* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::SerializableObjectWithMetadata*>(self)
                ->name();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void SerializableObjectWithMetadata_set_name(
        SerializableObjectWithMetadata* self, const char* name)
    {
        reinterpret_cast<OTIO_NS::SerializableObjectWithMetadata*>(self)
            ->set_name(name);
    }
    AnyDictionary* SerializableObjectWithMetadata_metadata(
        SerializableObjectWithMetadata* self)
    {
        OTIO_NS::AnyDictionary anyDictionary =
            reinterpret_cast<OTIO_NS::SerializableObjectWithMetadata*>(self)
                ->metadata();
        return reinterpret_cast<AnyDictionary*>(
            new OTIO_NS::AnyDictionary(anyDictionary));
    }
#ifdef __cplusplus
}
#endif
