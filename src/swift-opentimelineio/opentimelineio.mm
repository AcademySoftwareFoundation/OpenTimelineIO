//
//  opentimelineio.m
//  otio_macos
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>
#import "opentimelineio.h"
#import <opentimelineio/serializableObject.h>
#import <opentimelineio/serializableObjectWithMetadata.h>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

CxxRetainer* new_serializable_object() {
    auto r = [CxxRetainer new];
    r.retainer = new otio::SerializableObject;
    return r;
}

CxxRetainer* new_serializable_object_with_metadata(void* existing) {
    auto r = [CxxRetainer new];
    r.retainer = existing ? (otio::SerializableObjectWithMetadata*) existing : new otio::SerializableObjectWithMetadata;
    return r;
}

NSString* serializable_object_schema_name(CxxRetainer* r) {
    return [NSString stringWithUTF8String: serializableObject(r)->schema_name().c_str()];
}

NSString* serializable_object_to_json(CxxRetainer* r) {
    otio::ErrorStatus error_status;     // XXX
    return [NSString stringWithUTF8String: serializableObject(r)->to_json_string(&error_status).c_str()];
}

NSString* serializable_object_with_metadata_name(CxxRetainer* r) {
    return [NSString stringWithUTF8String: serializableObject<otio::SerializableObjectWithMetadata>(r)->name().c_str()];
}

void serializable_object_with_metadata_set_name(CxxRetainer* r, NSString* name) {
    serializableObject<otio::SerializableObjectWithMetadata>(r)->set_name([name UTF8String]);
}

void* serializable_object_special_object() {
    static auto held = otio::SerializableObject::Retainer<>(new otio::SerializableObjectWithMetadata);
    return held.value;
}
