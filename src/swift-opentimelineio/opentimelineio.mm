//
//  opentimelineio.m
//  otio_macos
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/composition.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/freezeFrame.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/generatorReference.h>
#include <opentimelineio/item.h>
#include <opentimelineio/linearTimeWarp.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/mediaReference.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/serializableCollection.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/serializableObjectWithMetadata.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/timeEffect.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>
#include <opentimelineio/transition.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/unknownSchema.h>

#import "opentimelineio.h"
#import "errorStruct.h"

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

static inline void deal_with_error(otio::ErrorStatus const& error_status, CxxErrorStruct* err) {
    if (error_status.outcome != error_status.OK) {
        err->statusCode = error_status.outcome;
        err->details = CFBridgingRetain([NSString stringWithUTF8String: error_status.full_description.c_str()]);
    }
}

template <typename T>
CxxRetainer* create_serializable_object() {
    auto r = [CxxRetainer new];
    r.retainer = new T;
    return r;
}

CxxRetainer* new_clip() {
    return create_serializable_object<otio::Clip>();
}

CxxRetainer* new_serializable_object() {
    return create_serializable_object<otio::SerializableObject>();
}

CxxRetainer* new_serializable_object_with_metadata() {
    return create_serializable_object<otio::SerializableObjectWithMetadata>();
}

CxxRetainer* new_composable() {
    return create_serializable_object<otio::Composable>();
}

CxxRetainer* new_composition() {
    return create_serializable_object<otio::Composition>();
}

CxxRetainer* new_effect() {
    return create_serializable_object<otio::Effect>();
}

CxxRetainer* new_external_reference() {
    return create_serializable_object<otio::ExternalReference>();
}

CxxRetainer* new_freeze_frame() {
    return create_serializable_object<otio::FreezeFrame>();
}

CxxRetainer* new_gap() {
    return create_serializable_object<otio::Gap>();
}

CxxRetainer* new_generator_reference() {
    return create_serializable_object<otio::GeneratorReference>();
}

CxxRetainer* new_item() {
    return create_serializable_object<otio::Item>();
}

CxxRetainer* new_linear_time_warp() {
    return create_serializable_object<otio::LinearTimeWarp>();
}

CxxRetainer* new_marker() {
    return create_serializable_object<otio::Marker>();
}

CxxRetainer* new_media_reference() {
    return create_serializable_object<otio::MediaReference>();
}

CxxRetainer* new_missing_reference() {
    return create_serializable_object<otio::MissingReference>();
}

CxxRetainer* new_serializable_collection() {
    return create_serializable_object<otio::SerializableCollection>();
}

CxxRetainer* new_stack() {
    return create_serializable_object<otio::Stack>();
}

CxxRetainer* new_time_effect() {
    return create_serializable_object<otio::TimeEffect>();
}

CxxRetainer* new_timeline() {
    return create_serializable_object<otio::Timeline>();
}

CxxRetainer* new_track() {
    return create_serializable_object<otio::Track>();
}

CxxRetainer* new_transition() {
    return create_serializable_object<otio::Transition>();
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
