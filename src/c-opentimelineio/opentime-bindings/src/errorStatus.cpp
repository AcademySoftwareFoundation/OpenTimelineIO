#include "copentime/errorStatus.h"
#include <opentime/errorStatus.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif

    OpenTimeErrorStatus* OpenTimeErrorStatus_create()
    {
        return reinterpret_cast<OpenTimeErrorStatus*>(
            new opentime::ErrorStatus());
    }
    OpenTimeErrorStatus* OpenTimeErrorStatus_create_with_outcome(
        OpenTime_ErrorStatus_Outcome in_outcome)
    {
        return reinterpret_cast<OpenTimeErrorStatus*>(new opentime::ErrorStatus(
            static_cast<opentime::ErrorStatus::Outcome>(in_outcome)));
    }
    OpenTimeErrorStatus* OpenTimeErrorStatus_create_with_outcome_and_details(
        OpenTime_ErrorStatus_Outcome in_outcome, const char* in_details)
    {
        return reinterpret_cast<OpenTimeErrorStatus*>(new opentime::ErrorStatus(
            static_cast<opentime::ErrorStatus::Outcome>(in_outcome),
            in_details));
    }
    const char* OpenTimeErrorStatus_outcome_to_string(
        OpenTimeErrorStatus* self, OpenTime_ErrorStatus_Outcome var1)
    {
        std::string returnStr = opentime::ErrorStatus::outcome_to_string(
            static_cast<opentime::ErrorStatus::Outcome>(var1));
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void OpenTimeErrorStatus_destroy(OpenTimeErrorStatus* self)
    {
        delete reinterpret_cast<opentime::ErrorStatus*>(self);
    }
#ifdef __cplusplus
}
#endif
