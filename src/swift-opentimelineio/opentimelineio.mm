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
#include <opentimelineio/stringUtils.h>

#import "opentimelineio.h"
#import "opentime.h"
#import "errorStruct.h"
#import "CxxVectorProperty.h"

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

template <typename T>
inline T* _Nonnull SO_cast(CxxRetainer const* r) {
    if (!r.retainer.value) {
        fprintf(stderr, "SO_cast [otio-swift] fatal error: dynamic cast to %s failed: underlying ptr is null\n",
                otio::demangled_type_name(typeid(T)).c_str());
        abort();
    }

    auto so = dynamic_cast<T*>(r.retainer.value);
    if (so) {
        return so;
    }

    fprintf(stderr, "SO_cast [otio-swift] fatal error: dynamic cast to %s failed: actual type was %s\n",
            otio::demangled_type_name(typeid(T)).c_str(),
            otio::demangled_type_name(r.retainer.value).c_str());
    abort();
}

static inline NSString* make_nsstring(std::string const& s) {
    return [NSString stringWithUTF8String: s.c_str()];
}

static inline void deal_with_error(otio::ErrorStatus const& error_status, CxxErrorStruct* err) {
    if (error_status.outcome != error_status.OK) {
        err->statusCode = error_status.outcome;
        err->details = CFBridgingRetain(make_nsstring(error_status.full_description));
    }
}

// MARK: - otio_new_XXX() methods

void* otio_new_clip() {
    otio::Clip* c = new otio::Clip;
    otio::AnyDictionary d, d2;
    d["abc"] = 123;
    d["xyz"] = 456;
    
    d2["r1"] = otio::RationalTime(1,2);
    d2["r2"] = otio::RationalTime(100,200);
    d2["plugh"] = 37;
    
    d["nested"] = d2;
    c->metadata() = d;
    return c;
}

void* otio_new_serializable_object() {
    return new otio::SerializableObject;
}

void* otio_new_serializable_object_with_metadata() {
    return new otio::SerializableObjectWithMetadata;
}

void* otio_new_composable() {
    return new otio::Composable;
}

void* otio_new_composition() {
    return new otio::Composition;
}

void* otio_new_effect() {
    return new otio::Effect;
}

void* otio_new_external_reference() {
    return new otio::ExternalReference;
}

void* otio_new_freeze_frame() {
    return new otio::FreezeFrame;
}

void* otio_new_gap() {
    return new otio::Gap;
}

void* otio_new_generator_reference() {
    return new otio::GeneratorReference;
}

void* otio_new_item() {
    return new otio::Item;
}

void* otio_new_linear_time_warp() {
    return new otio::LinearTimeWarp;
}

void* otio_new_marker() {
    return new otio::Marker;
}

void* otio_new_media_reference() {
    return new otio::MediaReference;
}

void* otio_new_missing_reference() {
    return new otio::MissingReference;
}

void* otio_new_serializable_collection() {
    return new otio::SerializableCollection;
}

void* otio_new_stack() {
    return new otio::Stack;
}

void* otio_new_time_effect() {
    return new otio::TimeEffect;
}

void* otio_new_timeline() {
    return new otio::Timeline;
}

void* otio_new_track() {
    return new otio::Track;
}

void* otio_new_transition() {
    return new otio::Transition;
}

// MARK: SerializableObject -----------------------------------------------------

void serializable_object_to_json_file(CxxRetainer* r, NSString* filename, int indent, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    r.retainer.value->to_json_file(filename.UTF8String, &error_status, indent);
    deal_with_error(error_status, cxxErr);
}

NSString* serializable_object_to_json_string(CxxRetainer* r, int indent, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto result = make_nsstring(r.retainer.value->to_json_string(&error_status, indent));
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
    auto result = r.retainer.value->clone(&error_status);
    deal_with_error(error_status, cxxErr);
    return result;
}
    
bool serializable_object_is_equivalent_to(CxxRetainer* lhs, CxxRetainer* rhs) {
    return lhs.retainer.value->is_equivalent_to(*rhs.retainer.value);
}

NSString* serializable_object_schema_name(CxxRetainer* r) {
    return make_nsstring(r.retainer.value->schema_name());
}

NSString* serializable_object_schema_name_from_ptr(void* cxxPtr) {
    auto so = reinterpret_cast<otio::SerializableObject*>(cxxPtr);
    return make_nsstring(so->schema_name());
}

int serializable_object_schema_version(CxxRetainer* r) {
    return r.retainer.value->schema_version();
}

bool serializable_object_is_unknown_schema(CxxRetainer* r) {
    return r.retainer.value->is_unknown_schema();
}

// MARK: - SerializableObject.Vector

void serializable_object_new_serializable_object_vector(CxxVectorProperty* p) {
    p.cxxVectorBase = new CxxSOVector<otio::SerializableObject>();
}

void serializable_object_new_marker_vector(CxxVectorProperty* p) {
    p.cxxVectorBase = new CxxSOVector<otio::Marker>();
}

void serializable_object_new_effect_vector(CxxVectorProperty* p) {
    p.cxxVectorBase = new CxxSOVector<otio::Effect>();
}

// MARK: - UnknownSchema

NSString* unknown_schema_original_schema_name(CxxRetainer* r) {
    return make_nsstring(SO_cast<otio::UnknownSchema>(r)->original_schema_name());
}

int unknown_schema_original_schema_version(CxxRetainer* r) {
    return SO_cast<otio::UnknownSchema>(r)->original_schema_version();
}

// MARK: - SerializableObjectWithMetadata

NSString* serializable_object_with_metadata_name(CxxRetainer* r) {
    return make_nsstring(SO_cast<otio::SerializableObjectWithMetadata>(r)->name());
}

void serializable_object_with_metadata_set_name(CxxRetainer* r, NSString* name) {
    SO_cast<otio::SerializableObjectWithMetadata>(r)->set_name([name UTF8String]);
}

void* serializable_object_with_metadata_metadata(CxxRetainer* r) {
    return &SO_cast<otio::SerializableObjectWithMetadata>(r)->metadata();
}

// MARK: - Composable
void* _Nullable  composable_parent(CxxRetainer* r) {
    return SO_cast<otio::Composable>(r)->parent();
}

bool composable_visible(CxxRetainer* r) {
    return SO_cast<otio::Composable>(r)->visible();
}

bool composable_overlapping(CxxRetainer* r) {
    return SO_cast<otio::Composable>(r)->overlapping();
}

// MARK: - Marker
NSString* marker_get_color(CxxRetainer* r) {
    return make_nsstring(SO_cast<otio::Marker>(r)->color());
    
}

void marker_set_color(CxxRetainer* r, NSString* color) {
    SO_cast<otio::Marker>(r)->set_color([color UTF8String]);
}

CxxTimeRange marker_get_marked_range(CxxRetainer* r) {
    return cxxTimeRange(SO_cast<otio::Marker>(r)->marked_range());
}

void marker_set_marked_range(CxxRetainer* r, CxxTimeRange cxxTimeRange) {
    SO_cast<otio::Marker>(r)->set_marked_range(otioTimeRange(cxxTimeRange));
}


// MARK: - Composition
CxxVectorProperty* create_composition_children_vector_property(CxxRetainer* composition_retainer) {
    auto composition = SO_cast<otio::Composition>(composition_retainer);
    auto p = [CxxVectorProperty new];
    
    // Yes, I know: but we're not going to mutate this and neither is anybody else.
    // We're only going to look at it.
    auto& children = const_cast<std::vector<otio::SerializableObject::Retainer<otio::Composable>>&>(composition->children());
    p.cxxVectorBase = new CxxSOVector<otio::Composable>(children);
    p.cxxRetainer = composition_retainer;
    return p;
}


// MARK: - SerializableCollection

CxxVectorProperty* create_serializable_collection_children_vector_property(CxxRetainer* sc_retainer) {
    auto sc = SO_cast<otio::SerializableCollection>(sc_retainer);
    auto p = [CxxVectorProperty new];
    p.cxxVectorBase = new CxxSOVector<otio::SerializableObject>(sc->children());
    p.cxxRetainer = sc_retainer;
    return p;
}

// MARK: - Item

CxxVectorProperty* create_item_markers_vector_property(CxxRetainer* item_retainer) {
    auto item = SO_cast<otio::Item>(item_retainer);
    auto p = [CxxVectorProperty new];
    p.cxxVectorBase = new CxxSOVector<otio::Marker>(item->markers());
    p.cxxRetainer = item_retainer;
    return p;
}

CxxVectorProperty* create_item_effects_vector_property(CxxRetainer* item_retainer) {
    auto item = SO_cast<otio::Item>(item_retainer);
    auto p = [CxxVectorProperty new];
    p.cxxVectorBase = new CxxSOVector<otio::Effect>(item->effects());
    p.cxxRetainer = item_retainer;
    return p;
}

bool item_get_source_range(CxxRetainer* item_retainer, CxxTimeRange* r) {
    auto item = SO_cast<otio::Item>(item_retainer);
    auto sr = item->source_range();
    if (sr) {
        *r = cxxTimeRange(*sr);
        return true;
    }
    return false;
}

void item_set_source_range(CxxRetainer* item_retainer , CxxTimeRange tr) {
    auto item = SO_cast<otio::Item>(item_retainer);
    item->set_source_range(otioTimeRange(tr));
}

void item_set_source_range_to_null(CxxRetainer* item_retainer) {
    auto item = SO_cast<otio::Item>(item_retainer);
    item->set_source_range(otio::optional<otio::TimeRange>());
}

CxxRationalTime item_duration(CxxRetainer* item_retainer, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxRationalTime(item->duration(&error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}

CxxTimeRange item_available_range(CxxRetainer* item_retainer, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxTimeRange(item->available_range(&error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}

CxxTimeRange item_trimmed_range(CxxRetainer* item_retainer, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxTimeRange(item->trimmed_range(&error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}

CxxTimeRange item_visible_range(CxxRetainer* item_retainer, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxTimeRange(item->visible_range(&error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}

bool item_trimmed_range_in_parent(CxxRetainer* item_retainer, CxxTimeRange* tr, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = item->trimmed_range_in_parent(&error_status);
    deal_with_error(error_status, cxxErr);
    if (result) {
        *tr = cxxTimeRange(*result);
        return true;
    }
    return false;
}

CxxTimeRange item_range_in_parent(CxxRetainer* item_retainer, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxTimeRange(item->range_in_parent(&error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}

CxxRationalTime item_transformed_time(CxxRetainer* item_retainer, CxxRationalTime rt, CxxRetainer* to_item, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxRationalTime(item->transformed_time(otioRationalTime(rt), SO_cast<otio::Item>(to_item), &error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}

CxxTimeRange item_transformed_time_range(CxxRetainer* item_retainer, CxxTimeRange tr, CxxRetainer* to_item, CxxErrorStruct* cxxErr) {
    otio::ErrorStatus error_status;
    auto item = SO_cast<otio::Item>(item_retainer);
    auto result = cxxTimeRange(item->transformed_time_range(otioTimeRange(tr), SO_cast<otio::Item>(to_item), &error_status));
    deal_with_error(error_status, cxxErr);
    return result;
}
