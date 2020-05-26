#include "copentimelineio/externalReference.h"
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/externalReference.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    ExternalReference* ExternalReference_create(
        const char*    target_url,
        TimeRange*     available_range,
        AnyDictionary* metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(available_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(available_range));
        }
        return reinterpret_cast<ExternalReference*>(
            new OTIO_NS::ExternalReference(
                target_url,
                timeRangeOptional,
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    const char* ExternalReference_target_url(ExternalReference* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::ExternalReference*>(self)->target_url();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void ExternalReference_set_target_url(
        ExternalReference* self, const char* target_url)
    {
        reinterpret_cast<OTIO_NS::ExternalReference*>(self)->set_target_url(
            target_url);
    }
#ifdef __cplusplus
}
#endif
