#include "copentimelineio/missingReference.h"
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/missingReference.h>

#ifdef __cplusplus
extern "C"
{
#endif
    MissingReference* MissingReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(available_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(available_range));
        }
        return reinterpret_cast<MissingReference*>(
            new OTIO_NS::MissingReference(
                name,
                timeRangeOptional,
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    _Bool MissingReference_is_missing_reference(MissingReference* self)
    {
        return reinterpret_cast<OTIO_NS::MissingReference*>(self)
            ->is_missing_reference();
    }
#ifdef __cplusplus
}
#endif
