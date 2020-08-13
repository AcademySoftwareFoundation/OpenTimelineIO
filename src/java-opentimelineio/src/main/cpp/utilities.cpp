#include <utilities.h>

std::map<std::type_info const *, std::string> getAnyType() {
    static std::once_flag typeFlag;
    static std::unique_ptr<std::map<std::type_info const *, std::string>> type_dispatch_table;
    std::call_once(typeFlag, []() {
        type_dispatch_table = std::unique_ptr<std::map<std::type_info const *, std::string >>(
                new std::map<std::type_info const *, std::string>());
        (*type_dispatch_table)[&typeid(bool)] = "java.lang.Boolean";
        (*type_dispatch_table)[&typeid(int)] = "java.lang.Integer";
        (*type_dispatch_table)[&typeid(long)] = "java.lang.Long";
        (*type_dispatch_table)[&typeid(double)] = "java.lang.Double";
        (*type_dispatch_table)[&typeid(std::string)] = "java.lang.String";
        (*type_dispatch_table)[&typeid(OTIO_NS::RationalTime)] = "io.opentimeline.opentime.RationalTime";
        (*type_dispatch_table)[&typeid(OTIO_NS::TimeRange)] = "io.opentimeline.opentime.TimeRange";
        (*type_dispatch_table)[&typeid(OTIO_NS::TimeTransform)] = "io.opentimeline.opentime.TimeTransform";
        (*type_dispatch_table)[&typeid(OTIO_NS::AnyDictionary)] = "io.opentimeline.opentimelineio.AnyDictionary";
        (*type_dispatch_table)[&typeid(OTIO_NS::AnyVector)] = "io.opentimeline.opentimelineio.AnyVector";
        (*type_dispatch_table)[&typeid(OTIO_NS::SerializableObject::Retainer<>)] = "io.opentimeline.opentimelineio.SerializableObject";
    });

    return *type_dispatch_table;
}

std::string getAnyType(const std::type_info &typeInfo) {
    if (typeInfo == typeid(bool))
        return "java.lang.Boolean";
    else if (typeInfo == typeid(int))
        return "java.lang.Integer";
    else if (typeInfo == typeid(long))
        return "java.lang.Long";
    else if (typeInfo == typeid(double))
        return "java.lang.Double";
    else if (typeInfo == typeid(std::string))
        return "java.lang.String";
    else if (typeInfo == typeid(OTIO_NS::RationalTime))
        return "io.opentimeline.opentime.RationalTime";
    else if (typeInfo == typeid(OTIO_NS::TimeRange))
        return "io.opentimeline.opentime.TimeRange";
    else if (typeInfo == typeid(OTIO_NS::TimeTransform))
        return "io.opentimeline.opentime.TimeTransform";
    else if (typeInfo == typeid(OTIO_NS::AnyDictionary))
        return "io.opentimeline.opentimelineio.AnyDictionary";
    else if (typeInfo == typeid(OTIO_NS::AnyVector))
        return "io.opentimeline.opentimelineio.AnyVector";
    else if (typeInfo == typeid(OTIO_NS::SerializableObject::Retainer<>))
        return "io.opentimeline.opentimelineio.SerializableObject";
    else
        return "";
}