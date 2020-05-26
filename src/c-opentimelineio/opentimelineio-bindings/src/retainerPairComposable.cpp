#include "copentimelineio/retainerPairComposable.h"
#include <opentimelineio/composable.h>
#include <utility>

typedef std::pair<
    OTIO_NS::Composable::Retainer<OTIO_NS::Composable>,
    OTIO_NS::Composable::Retainer<OTIO_NS::Composable>>
    PairDef;
typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>
    ComposableRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    RetainerPairComposable* RetainerPairComposable_create(
        RetainerComposable* first, RetainerComposable* second)
    {
        ComposableRetainer firstComposableRetainer =
            *reinterpret_cast<ComposableRetainer*>(first);
        ComposableRetainer secondComposableRetainer =
            *reinterpret_cast<ComposableRetainer*>(second);
        return reinterpret_cast<RetainerPairComposable*>(
            new PairDef(firstComposableRetainer, secondComposableRetainer));
    }
    RetainerComposable*
    RetainerPairComposable_first(RetainerPairComposable* self)
    {
        ComposableRetainer composableRetainer =
            reinterpret_cast<PairDef*>(self)->first;
        return reinterpret_cast<RetainerComposable*>(
            new ComposableRetainer(composableRetainer));
    }
    RetainerComposable*
    RetainerPairComposable_second(RetainerPairComposable* self)
    {
        ComposableRetainer composableRetainer =
            reinterpret_cast<PairDef*>(self)->second;
        return reinterpret_cast<RetainerComposable*>(
            new ComposableRetainer(composableRetainer));
    }
    void RetainerPairComposable_destroy(RetainerPairComposable* self)
    {
        delete reinterpret_cast<PairDef*>(self);
    }

#ifdef __cplusplus
}
#endif
