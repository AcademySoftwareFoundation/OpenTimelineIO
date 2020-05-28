#include "copentimelineio/any.h"
#include <opentimelineio/any.h>
#include <opentimelineio/version.h>

#ifdef __cplusplus
extern "C"
{
#endif

    void Any_destroy(Any* self)
    {
        delete reinterpret_cast<OTIO_NS::any*>(self);
    }

#ifdef __cplusplus
}
#endif