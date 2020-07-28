#include <class_codes.h>

std::map<std::string, ClassCode> stringToClassCode = {
    { "io.opentimeline.opentimelineio.Any", ClassCode::_Any },
    { "io.opentimeline.opentime.ErrorStatus", ClassCode::_OpenTimeErrorStatus },
    { "io.opentimeline.opentimelineio.ErrorStatus",
        ClassCode::_OTIOErrorStatus },
    { "io.opentimeline.opentimelineio.SerializableObject",
        ClassCode::_SerializableObject },
};

std::map<ClassCode, std::string> classCodeToString = {
    { ClassCode::_Any, "io.opentimeline.opentimelineio.Any" },
    { ClassCode::_OpenTimeErrorStatus, "io.opentimeline.opentime.ErrorStatus" },
    { ClassCode::_OTIOErrorStatus,
        "io.opentimeline.opentimelineio.ErrorStatus" },
    { ClassCode::_SerializableObject,
        "io.opentimeline.opentimelineio.SerializableObject" },
};