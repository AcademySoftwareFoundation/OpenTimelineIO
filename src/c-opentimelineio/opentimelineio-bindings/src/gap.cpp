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
        return reinterpret_cast<Gap*>(new OTIO_NS::Gap(
            *reinterpret_cast<opentime::TimeRange*>(source_range),
            name,
            *reinterpret_cast<EffectVectorDef*>(effects),
            *reinterpret_cast<MarkerVectorDef*>(markers),
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
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