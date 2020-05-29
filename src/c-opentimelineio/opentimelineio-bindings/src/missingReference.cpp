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
        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        std::string name_str = std::string();
        if(name != NULL) name_str = name;
        return reinterpret_cast<MissingReference*>(
            new OTIO_NS::MissingReference(
                name_str, timeRangeOptional, metadataDictionary));
    }
    _Bool MissingReference_is_missing_reference(MissingReference* self)
    {
        return reinterpret_cast<OTIO_NS::MissingReference*>(self)
            ->is_missing_reference();
    }
#ifdef __cplusplus
}
#endif
