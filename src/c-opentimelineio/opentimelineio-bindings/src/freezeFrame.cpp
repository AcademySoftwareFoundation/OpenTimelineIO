#include "copentimelineio/freezeFrame.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/freezeFrame.h>

#ifdef __cplusplus
extern "C"
{
#endif
    FreezeFrame* FreezeFrame_create(const char* name, AnyDictionary* metadata)
    {
        return reinterpret_cast<FreezeFrame*>(new OTIO_NS::FreezeFrame(
            name, *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
#ifdef __cplusplus
}
#endif
