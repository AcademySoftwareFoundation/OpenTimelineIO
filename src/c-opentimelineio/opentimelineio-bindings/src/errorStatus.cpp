#include "copentimelineio/errorStatus.h"
#include <opentimelineio/errorStatus.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif

    OTIOErrorStatus* OTIOErrorStatus_create()
    {
        return reinterpret_cast<OTIOErrorStatus*>(new OTIO_NS::ErrorStatus());
    }
    OTIOErrorStatus*
    OTIOErrorStatus_create_with_outcome(OTIO_ErrorStatus_Outcome in_outcome)
    {
        return reinterpret_cast<OTIOErrorStatus*>(new OTIO_NS::ErrorStatus(
            static_cast<OTIO_NS::ErrorStatus::Outcome>(in_outcome)));
    }
    OTIOErrorStatus*
    OTIOErrorStatus_create_with_outcome_details_serializable_object(
        OTIO_ErrorStatus_Outcome in_outcome,
        const char*              in_details,
        SerializableObject*      object)
    {
        return reinterpret_cast<OTIOErrorStatus*>(new OTIO_NS::ErrorStatus(
            static_cast<OTIO_NS::ErrorStatus::Outcome>(in_outcome),
            in_details,
            reinterpret_cast<OTIO_NS::SerializableObject*>(object)));
    }
    const char* OTIOErrorStatus_outcome_to_string(OTIO_ErrorStatus_Outcome var1)
    {
        std::string returnStr = OTIO_NS::ErrorStatus::outcome_to_string(
            static_cast<OTIO_NS::ErrorStatus::Outcome>(var1));
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    OTIO_ErrorStatus_Outcome OTIOErrorStatus_get_outcome(OTIOErrorStatus* self)
    {
        return static_cast<OTIO_ErrorStatus_Outcome>(
            reinterpret_cast<OTIO_NS::ErrorStatus*>(self)->outcome);
    }
    void OTIOErrorStatus_destroy(OTIOErrorStatus* self)
    {
        delete reinterpret_cast<OTIO_NS::ErrorStatus*>(self);
    }
#ifdef __cplusplus
}
#endif