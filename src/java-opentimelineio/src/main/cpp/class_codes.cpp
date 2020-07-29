#include <class_codes.h>

std::map<std::string, ClassCode> stringToClassCode = {
        {"io.opentimeline.opentimelineio.Any",   ClassCode::_Any},
        {"io.opentimeline.opentime.ErrorStatus", ClassCode::_OpenTimeErrorStatus},
        {"io.opentimeline.opentimelineio.ErrorStatus",
                                                 ClassCode::_OTIOErrorStatus},
        {"io.opentimeline.opentimelineio.SerializableObject",
                                                 ClassCode::_SerializableObject},
        {"io.opentimeline.opentimelineio.SerializableObjectWithMetadata",
                                                 ClassCode::_SerializableObjectWithMetadata},
        {"io.opentimeline.opentimelineio.SerializableCollection",
                                                 ClassCode::_SerializableCollection},
        {"io.opentimeline.opentimelineio.Composable",
                                                 ClassCode::_Composable},
        {"io.opentimeline.opentimelineio.Marker",
                                                 ClassCode::_Marker},
        {"io.opentimeline.opentimelineio.MediaReference",
                                                 ClassCode::_MediaReference},
};

std::map<ClassCode, std::string> classCodeToString = {
        {ClassCode::_Any,                 "io.opentimeline.opentimelineio.Any"},
        {ClassCode::_OpenTimeErrorStatus, "io.opentimeline.opentime.ErrorStatus"},
        {ClassCode::_OTIOErrorStatus,
                                          "io.opentimeline.opentimelineio.ErrorStatus"},
        {ClassCode::_SerializableObject,
                                          "io.opentimeline.opentimelineio.SerializableObject"},
        {ClassCode::_SerializableObjectWithMetadata,
                                          "io.opentimeline.opentimelineio.SerializableObjectWithMetadata"},
        {ClassCode::_SerializableCollection,
                                          "io.opentimeline.opentimelineio.SerializableCollection"},
        {ClassCode::_Composable,
                                          "io.opentimeline.opentimelineio.Composable"},
        {ClassCode::_Marker,
                                          "io.opentimeline.opentimelineio.Marler"},
        {ClassCode::_MediaReference,
                                          "io.opentimeline.opentimelineio.MediaReference"},
};