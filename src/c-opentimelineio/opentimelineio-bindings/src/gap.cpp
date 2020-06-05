#include "copentimelineio/gap.h"
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/gap.h>

typedef std::vector<OTIO_NS::Effect*>           EffectVectorDef;
typedef std::vector<OTIO_NS::Effect*>::iterator EffectVectorIteratorDef;
typedef std::vector<OTIO_NS::Marker*>           MarkerVectorDef;
typedef std::vector<OTIO_NS::Marker*>::iterator MarkerVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    Gap* Gap_create_with_source_range(
        TimeRange*     source_range,
        const char*    name,
        EffectVector*  effects,
        MarkerVector*  markers,
        AnyDictionary* metadata)
    {
        OTIO_NS::TimeRange source_range_tr = OTIO_NS::TimeRange();
        if(source_range != NULL)
            source_range_tr =
                *reinterpret_cast<opentime::TimeRange*>(source_range);
        std::string name_str = std::string();
        if(name != NULL) name_str = name;
        EffectVectorDef effectVectorDef = EffectVectorDef();
        if(effects != NULL)
            effectVectorDef = *reinterpret_cast<EffectVectorDef*>(effects);
        MarkerVectorDef markerVectorDef = MarkerVectorDef();
        if(markers != NULL)
            markerVectorDef = *reinterpret_cast<MarkerVectorDef*>(markers);
        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<Gap*>(new OTIO_NS::Gap(
            source_range_tr,
            name_str,
            effectVectorDef,
            markerVectorDef,
            metadataDictionary));
    }
    Gap* Gap_create_with_duration(
        RationalTime*  duration,
        const char*    name,
        EffectVector*  effects,
        MarkerVector*  markers,
        AnyDictionary* metadata)
    {
        return reinterpret_cast<Gap*>(new OTIO_NS::Gap(
            *reinterpret_cast<opentime::RationalTime*>(duration),
            name,
            *reinterpret_cast<EffectVectorDef*>(effects),
            *reinterpret_cast<MarkerVectorDef*>(markers),
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    _Bool Gap_visible(Gap* self)
    {
        return reinterpret_cast<OTIO_NS::Gap*>(self)->visible();
    }
#ifdef __cplusplus
}
#endif