#include "copentimelineio/linearTimeWarp.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/linearTimeWarp.h>

#ifdef __cplusplus
extern "C"
{
#endif
    LinearTimeWarp* LinearTimeWarp_create(
        const char*    name,
        const char*    effect_name,
        double         time_scalar,
        AnyDictionary* metadata)
    {
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        std::string effect_name_str = "LinearTimeWarp";
        if(effect_name != NULL) effect_name_str = effect_name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<LinearTimeWarp*>(new OTIO_NS::LinearTimeWarp(
            name_str, effect_name_str, time_scalar, metadataDictionary));
    }
    double LinearTimeWarp_time_scalar(LinearTimeWarp* self)
    {
        return reinterpret_cast<OTIO_NS::LinearTimeWarp*>(self)->time_scalar();
    }
    void
    LinearTimeWarp_set_time_scalar(LinearTimeWarp* self, double time_scalar)
    {
        reinterpret_cast<OTIO_NS::LinearTimeWarp*>(self)->set_time_scalar(
            time_scalar);
    }
#ifdef __cplusplus
}
#endif
