#include <map>

#ifndef _CLASS_CODES_H_INCLUDED_
#define _CLASS_CODES_H_INCLUDED_

enum ClassCode {
    _OpenTimeErrorStatus,
    _Any,
    _OTIOErrorStatus,
    _SerializableObject,
    _SerializableObjectWithMetadata,
    _SerializableCollection,
    _Composable,
    _Marker,
    _MediaReference,
};

extern std::map<std::string, ClassCode> stringToClassCode;

extern std::map<ClassCode, std::string> classCodeToString;

#endif