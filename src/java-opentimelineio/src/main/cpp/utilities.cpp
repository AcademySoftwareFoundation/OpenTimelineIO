#include <utilities.h>

std::map<std::type_info const *, std::string> _type_dispatch_table = {
        {&typeid(bool), "java.lang.Boolean"},
        {&typeid(int), "java.lang.Integer"},
        {&typeid(long), "java.lang.Long"},
        {&typeid(double), "java.lang.Double"},
        {&typeid(std::string), "java.lang.String"},
        {&typeid(OTIO_NS::RationalTime), "io.opentimeline.opentime.RationalTime"},
        {&typeid(OTIO_NS::TimeRange), "io.opentimeline.opentime.TimeRange"},
        {&typeid(OTIO_NS::TimeTransform), "io.opentimeline.opentime.TimeTransform"},
        {&typeid(OTIO_NS::AnyDictionary), "io.opentimeline.opentimelineio.AnyDictionary"},
        {&typeid(OTIO_NS::AnyVector), "io.opentimeline.opentimelineio.AnyVector"},
        {&typeid(OTIO_NS::SerializableObject::Retainer<>), "io.opentimeline.opentimelineio.SerializableObject"},
};