//
//  opentimelineio.m
//  otio_macos
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>
#import <opentimelineio/serializableObject.h>
#import <opentimelineio/serializableObjectWithMetadata.h>
#import <opentimelineio/clip.h>

#import "opentimelineio.h"
#import "errorStruct.h"

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

static inline void deal_with_error(otio::ErrorStatus const& error_status, CxxErrorStruct* err) {
    if (error_status.outcome != error_status.OK) {
        err->statusCode = error_status.outcome;
        err->details = CFBridgingRetain([NSString stringWithUTF8String: error_status.details.c_str()]);
    }
}

template <typename T>
CxxRetainer* create_serializable_object() {
    auto r = [CxxRetainer new];
    r.retainer = new T;
    return r;
}

CxxRetainer* new_serializable_object() {
    return create_serializable_object<otio::SerializableObject>();
}

CxxRetainer* new_serializable_object_with_metadata() {
    return create_serializable_object<otio::SerializableObjectWithMetadata>();
}

CxxRetainer* new_clip() {
    return create_serializable_object<otio::Clip>();
}

// SerializableObject -----------------------------------------------------

void serializable_object_to_json_file(CxxRetainer* r, NSString* filename, int indent, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    serializableObject(r)->to_json_file(filename.UTF8String, &error_status, indent);
    deal_with_error(error_status, cxxErr);
}

NSString* serializable_object_to_json_string(CxxRetainer* r, int indent, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto result = [NSString stringWithUTF8String: serializableObject(r)->to_json_string(&error_status, indent).c_str()];
    deal_with_error(error_status, cxxErr);
    return result;
}

void* serializable_object_from_json_string(NSString* input, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto result = otio::SerializableObject::from_json_string(input.UTF8String, &error_status);
    deal_with_error(error_status, cxxErr);
    return result;
}

void* serializable_object_from_json_file(NSString* filename, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto result = otio::SerializableObject::from_json_file(filename.UTF8String, &error_status);
    deal_with_error(error_status, cxxErr);
    return result;
}

void* serializable_object_clone(CxxRetainer* r, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto result = serializableObject(r)->clone(&error_status);
    deal_with_error(error_status, cxxErr);
    return result;
}
    
bool serializable_object_is_equivalent_to(CxxRetainer* lhs, CxxRetainer* rhs) {
    return serializableObject(lhs)->is_equivalent_to(*serializableObject(rhs));
}

NSString* serializable_object_schema_name(CxxRetainer* r) {
    return [NSString stringWithUTF8String: serializableObject(r)->schema_name().c_str()];
}

int serializable_object_schema_version(CxxRetainer* r) {
    return serializableObject(r)->schema_version();
}

// SerializableObjectWithMetadata -----------------------------------------------------

NSString* serializable_object_with_metadata_name(CxxRetainer* r) {
    return [NSString stringWithUTF8String: serializableObject<otio::SerializableObjectWithMetadata>(r)->name().c_str()];
}

bool serializable_object_is_unknown_schema(CxxRetainer* r) {
    return r.retainer.value->is_unknown_schema();
}

void serializable_object_with_metadata_set_name(CxxRetainer* r, NSString* name) {
    serializableObject<otio::SerializableObjectWithMetadata>(r)->set_name([name UTF8String]);
}
