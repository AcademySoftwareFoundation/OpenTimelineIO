#include "copentimelineio/freezeFrame.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/freezeFrame.h>

#ifdef __cplusplus
extern "C"
{
#endif
    FreezeFrame* FreezeFrame_create(const char* name, AnyDictionary* metadata)
    {
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<FreezeFrame*>(
            new OTIO_NS::FreezeFrame(name_str, metadataDictionary));
    }
#ifdef __cplusplus
}
#endif
