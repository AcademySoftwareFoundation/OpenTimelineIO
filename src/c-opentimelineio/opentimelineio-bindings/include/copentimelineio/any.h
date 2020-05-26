#pragma once

#ifdef __cplusplus
extern "C"
{
#endif

    struct Any;
    typedef struct Any Any;

    Any* Any_create(int a);
    void Any_destroy(Any* self);

#ifdef __cplusplus
}
#endif