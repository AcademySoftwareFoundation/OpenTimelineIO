//
//  CxxAny.h
//  otio-swift
//
//  Created by David Baraff on 2/21/19.
//

#import "opentime.h"

#if defined(__cplusplus)
#import <opentimelineio/any.h>
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
#endif

typedef union CxxAnyValue {
    bool b;
    int64_t i;
    double d;
    char const* s;
    void* ptr;
    CxxRationalTime rt;
    CxxTimeRange tr;
    CxxTimeTransform tt;
} CxxAnyValue;

typedef struct CxxAny {
    enum {
        NONE = 0,
        BOOL,
        INT,
        DOUBLE,
        STRING,
        SERIALIZABLE_OBJECT,
        RATIONAL_TIME,
        TIME_RANGE,
        TIME_TRANSFORM,
        DICTIONARY,
        VECTOR,
        UNKNOWN
    };
    
    int type_code;
    CxxAnyValue value;
} CxxAny;

#if defined(__cplusplus)
void otio_any_to_cxx_any(otio::any const&, CxxAny*);
otio::any cxx_any_to_otio_any(CxxAny const&);
#endif
