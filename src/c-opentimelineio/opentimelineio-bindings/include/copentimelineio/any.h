#pragma once

#ifdef __cplusplus
extern "C"
{
#endif

    struct Any;
    typedef struct Any Any;

    void Any_destroy(Any* self);

#ifdef __cplusplus
}
#endif