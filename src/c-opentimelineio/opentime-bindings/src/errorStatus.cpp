#include "copentime/errorStatus.h"
#include <opentime/errorStatus.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif

    ErrorStatus* ErrorStatus_create()
    {
        return reinterpret_cast<ErrorStatus*>(new opentime::ErrorStatus());
    }
    ErrorStatus*
    ErrorStatus_create_with_outcome(OTIO_ErrorStatus_Outcome in_outcome)
    {
        return reinterpret_cast<ErrorStatus*>(new opentime::ErrorStatus(
            static_cast<opentime::ErrorStatus::Outcome>(in_outcome)));
    }
    ErrorStatus* ErrorStatus_create_with_outcome_and_details(
        OTIO_ErrorStatus_Outcome in_outcome, const char* in_details)
    {
        return reinterpret_cast<ErrorStatus*>(new opentime::ErrorStatus(
            static_cast<opentime::ErrorStatus::Outcome>(in_outcome),
            in_details));
    }
    const char* ErrorStatus_outcome_to_string(
        ErrorStatus* self, OTIO_ErrorStatus_Outcome var1)
    {
        std::string returnStr = opentime::ErrorStatus::outcome_to_string(
            static_cast<opentime::ErrorStatus::Outcome>(var1));
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void ErrorStatus_destroy(ErrorStatus* self)
    {
        delete reinterpret_cast<opentime::ErrorStatus*>(self);
    }
#ifdef __cplusplus
}
#endif
