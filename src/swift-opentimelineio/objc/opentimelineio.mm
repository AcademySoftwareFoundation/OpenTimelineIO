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
#include <opentimelineio/trackAlgorithm.h>
#include <opentimelineio/stackAlgorithm.h>

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

struct _AutoErrorHandler {
    _AutoErrorHandler(CxxErrorStruct* cxxErr) : _cxxErr {cxxErr} { }

    ~_AutoErrorHandler() {
        if (error_status.outcome != error_status.OK) {
            _cxxErr->statusCode = error_status.outcome;
            _cxxErr->details = CFBridgingRetain(make_nsstring(error_status.full_description));
        }
    }

    otio::ErrorStatus error_status;
    CxxErrorStruct* _cxxErr;
};

// MARK: - otio_new_XXX() methods

void* otio_new_clip() {
    return new otio::Clip;
    /*
    otio::Clip* c = new otio::Clip;
    otio::AnyDictionary d, d2;
    d["abc"] = 123;
    d["xyz"] = 456;
    
    d2["r1"] = otio::RationalTime(1,2);
    d2["r2"] = otio::RationalTime(100,200);
    d2["plugh"] = 37;
    
    d["nested"] = d2;
    c->metadata() = d;
    return c;*/
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

// MARK: - SerializableObject

void serializable_object_to_json_file(CxxRetainer* self, NSString* filename, int indent, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    self.retainer.value->to_json_file(filename.UTF8String, &aeh.error_status, indent);
    
}

NSString* serializable_object_to_json_string(CxxRetainer* self, int indent, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return make_nsstring(self.retainer.value->to_json_string(&aeh.error_status, indent));
}

void* serializable_object_from_json_string(NSString* input, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return otio::SerializableObject::from_json_string(input.UTF8String, &aeh.error_status);
}

void* serializable_object_from_json_file(NSString* filename, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return otio::SerializableObject::from_json_file(filename.UTF8String, &aeh.error_status);
}

void* serializable_object_clone(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return self.retainer.value->clone(&aeh.error_status);
}
    
bool serializable_object_is_equivalent_to(CxxRetainer* lhs, CxxRetainer* rhs) {
    return lhs.retainer.value->is_equivalent_to(*rhs.retainer.value);
}

NSString* serializable_object_schema_name(CxxRetainer* self) {
    return make_nsstring(self.retainer.value->schema_name());
}

NSString* serializable_object_schema_name_from_ptr(void* cxxPtr) {
    auto so = reinterpret_cast<otio::SerializableObject*>(cxxPtr);
    return make_nsstring(so->schema_name());
}

int serializable_object_schema_version(CxxRetainer* self) {
    return self.retainer.value->schema_version();
}

bool serializable_object_is_unknown_schema(CxxRetainer* self) {
    return self.retainer.value->is_unknown_schema();
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

NSString* unknown_schema_original_schema_name(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::UnknownSchema>(self)->original_schema_name());
}

int unknown_schema_original_schema_version(CxxRetainer* self) {
    return SO_cast<otio::UnknownSchema>(self)->original_schema_version();
}

// MARK: - SerializableObjectWithMetadata

NSString* serializable_object_with_metadata_name(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::SerializableObjectWithMetadata>(self)->name());
}

void serializable_object_with_metadata_set_name(CxxRetainer* self, NSString* name) {
    SO_cast<otio::SerializableObjectWithMetadata>(self)->set_name([name UTF8String]);
}

void* serializable_object_with_metadata_metadata(CxxRetainer* self) {
    return &SO_cast<otio::SerializableObjectWithMetadata>(self)->metadata();
}

// MARK: - Composable
void* composable_parent(CxxRetainer* self) {
    return SO_cast<otio::Composable>(self)->parent();
}

bool composable_visible(CxxRetainer* self) {
    return SO_cast<otio::Composable>(self)->visible();
}

bool composable_overlapping(CxxRetainer* self) {
    return SO_cast<otio::Composable>(self)->overlapping();
}

CxxRationalTime composable_duration(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return cxxRationalTime(SO_cast<otio::Composable>(self)->duration(&aeh.error_status));
}


// MARK: - Marker
NSString* marker_get_color(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::Marker>(self)->color());
}

void marker_set_color(CxxRetainer* self, NSString* color) {
    SO_cast<otio::Marker>(self)->set_color([color UTF8String]);
}

CxxTimeRange marker_get_marked_range(CxxRetainer* self) {
    return cxxTimeRange(SO_cast<otio::Marker>(self)->marked_range());
}

void marker_set_marked_range(CxxRetainer* self, CxxTimeRange cxxTimeRange) {
    SO_cast<otio::Marker>(self)->set_marked_range(otioTimeRange(cxxTimeRange));
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

CxxVectorProperty* create_item_markers_vector_property(CxxRetainer* self) {
    auto item = SO_cast<otio::Item>(self);
    auto p = [CxxVectorProperty new];
    p.cxxVectorBase = new CxxSOVector<otio::Marker>(item->markers());
    p.cxxRetainer = self;
    return p;
}

CxxVectorProperty* create_item_effects_vector_property(CxxRetainer* self) {
    auto item = SO_cast<otio::Item>(self);
    auto p = [CxxVectorProperty new];
    p.cxxVectorBase = new CxxSOVector<otio::Effect>(item->effects());
    p.cxxRetainer = self;
    return p;
}

bool item_get_source_range(CxxRetainer* self, CxxTimeRange* r) {
    auto item = SO_cast<otio::Item>(self);
    auto sr = item->source_range();
    if (sr) {
        *r = cxxTimeRange(*sr);
        return true;
    }
    return false;
}

void item_set_source_range(CxxRetainer* self , CxxTimeRange tr) {
    auto item = SO_cast<otio::Item>(self);
    item->set_source_range(otioTimeRange(tr));
}

void item_set_source_range_to_null(CxxRetainer* self) {
    auto item = SO_cast<otio::Item>(self);
    item->set_source_range(otio::optional<otio::TimeRange>());
}

CxxTimeRange item_available_range(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    return cxxTimeRange(item->available_range(&aeh.error_status));
}

CxxTimeRange item_trimmed_range(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    return cxxTimeRange(item->trimmed_range(&aeh.error_status));
}

CxxTimeRange item_visible_range(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    return cxxTimeRange(item->visible_range(&aeh.error_status));
}

bool item_trimmed_range_in_parent(CxxRetainer* self, CxxTimeRange* tr, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    auto result = item->trimmed_range_in_parent(&aeh.error_status);
    
    if (result) {
        *tr = cxxTimeRange(*result);
        return true;
    }
    return false;
}

CxxTimeRange item_range_in_parent(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    return cxxTimeRange(item->range_in_parent(&aeh.error_status));
}

CxxRationalTime item_transformed_time(CxxRetainer* self, CxxRationalTime rt, CxxRetainer* to_item, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    return cxxRationalTime(item->transformed_time(otioRationalTime(rt),
                                                  SO_cast<otio::Item>(to_item), &aeh.error_status));
}

CxxTimeRange item_transformed_time_range(CxxRetainer* self, CxxTimeRange tr, CxxRetainer* to_item, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto item = SO_cast<otio::Item>(self);
    return cxxTimeRange(item->transformed_time_range(otioTimeRange(tr), SO_cast<otio::Item>(to_item),
                                                     &aeh.error_status));
}

// MARK: - Transition
CxxRationalTime transition_get_in_offset(CxxRetainer* self) {
    return cxxRationalTime(SO_cast<otio::Transition>(self)->in_offset());
}

void transition_set_in_offset(CxxRetainer* self, CxxRationalTime rt) {
    return SO_cast<otio::Transition>(self)->set_in_offset(otioRationalTime(rt));
}

CxxRationalTime transition_get_out_offset(CxxRetainer* self) {
    return cxxRationalTime(SO_cast<otio::Transition>(self)->out_offset());
}

void transition_set_out_offset(CxxRetainer* self, CxxRationalTime rt) {
    return SO_cast<otio::Transition>(self)->set_out_offset(otioRationalTime(rt));
}

NSString* transition_get_transition_type(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::Transition>(self)->transition_type());
}

void transition_set_transition_type(CxxRetainer* self, NSString* transitionType) {
     SO_cast<otio::Transition>(self)->set_transition_type([transitionType UTF8String]);
}

bool transition_range_in_parent(CxxRetainer* self, CxxTimeRange* tr, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto result = SO_cast<otio::Transition>(self)->range_in_parent(&aeh.error_status);
    if (result) {
        *tr = cxxTimeRange(*result);
        return true;
    }
    return false;
}

bool transition_trimmed_range_in_parent(CxxRetainer* self, CxxTimeRange* tr, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto result = SO_cast<otio::Transition>(self)->trimmed_range_in_parent(&aeh.error_status);
    if (result) {
        *tr = cxxTimeRange(*result);
        return true;
    }
    return false;
}

// MARK: - Clip
void* clip_media_reference(CxxRetainer* self) {
    return SO_cast<otio::Clip>(self)->media_reference();
}

void clip_set_media_reference(CxxRetainer* self, CxxRetainer* media_reference) {
    otio::MediaReference* mr = media_reference ? SO_cast<otio::MediaReference>(media_reference) : nullptr;
    return SO_cast<otio::Clip>(self)->set_media_reference(mr);
}

// MARK: - Composition
CxxVectorProperty* create_composition_children_vector_property(CxxRetainer* self) {
    auto composition = SO_cast<otio::Composition>(self);
    auto p = [CxxVectorProperty new];
    
    // Yes, I know: but we're not going to mutate this and neither is anybody else.
    // We're only going to look at it.
    auto& children = const_cast<std::vector<otio::SerializableObject::Retainer<otio::Composable>>&>(composition->children());
    p.cxxVectorBase = new CxxSOVector<otio::Composable>(children);
    p.cxxRetainer = self;
    return p;
}

void composition_remove_all_children(CxxRetainer* self) {
    auto composition = SO_cast<otio::Composition>(self);
    composition->clear_children();
}

void composition_replace_child(CxxRetainer* self, int index, CxxRetainer* child_retainer, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto composition = SO_cast<otio::Composition>(self);
    composition->set_child(index, SO_cast<otio::Composable>(child_retainer), &aeh.error_status);
}

void composition_insert_child(CxxRetainer* self, int index, CxxRetainer* child_retainer, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto composition = SO_cast<otio::Composition>(self);
    composition->insert_child(index, SO_cast<otio::Composable>(child_retainer), &aeh.error_status);
}

void composition_remove_child(CxxRetainer* self, int index, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto composition = SO_cast<otio::Composition>(self);
    composition->remove_child(index, &aeh.error_status);
}

void composition_append_child(CxxRetainer* self, CxxRetainer* child_retainer, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto composition = SO_cast<otio::Composition>(self);
    composition->append_child(SO_cast<otio::Composable>(child_retainer), &aeh.error_status);
}

NSDictionary* composition_range_of_all_children(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    auto dict = [NSMutableDictionary new];
    _AutoErrorHandler aeh(cxxErr);
    auto result = SO_cast<otio::Composition>(self)->range_of_all_children(&aeh.error_status);
    
    for (auto item: result) {
        auto tr = cxxTimeRange(item.second);
        [dict setObject: [NSValue valueWithBytes:&tr objCType:@encode(CxxTimeRange)]
                 forKey: [NSValue valueWithPointer:item.first]];
    }
    
    return dict;
}

NSString* composition_composition_kind(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::Composition>(self)->composition_kind());
}

bool composition_is_parent_of(CxxRetainer* self, CxxRetainer* composable) {
    return SO_cast<otio::Composition>(self)->is_parent_of(SO_cast<otio::Composable>(composable));
}

bool composition_has_child(CxxRetainer* self, CxxRetainer* composable) {
    return SO_cast<otio::Composition>(self)->has_child(SO_cast<otio::Composable>(composable));
}

void composition_handles_of_child(CxxRetainer* self, CxxRetainer* composable,
                                 CxxRationalTime* rt1, CxxRationalTime* rt2,
                                 bool* hasLeft, bool* hasRight, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto result = SO_cast<otio::Composition>(self)->handles_of_child(SO_cast<otio::Composable>(composable), &aeh.error_status);
    
    if (result.first) {
        *hasLeft = true;
        *rt1 = cxxRationalTime(*(result.first));
    }
    else {
        *hasLeft = false;
    }
    
    if (result.second) {
        *hasRight = true;
        *rt2 = cxxRationalTime(*(result.second));
    }
    else {
        *hasRight = false;
    }
}

CxxTimeRange composition_range_of_child_at_index(CxxRetainer* self, int index,
                                        CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return cxxTimeRange(SO_cast<otio::Composition>(self)->range_of_child_at_index(index, &aeh.error_status));
}

CxxTimeRange composition_trimmed_range_of_child_at_index(CxxRetainer* self, int index,
                                        CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return cxxTimeRange(SO_cast<otio::Composition>(self)->trimmed_range_of_child_at_index(index, &aeh.error_status));
}

bool composition_trim_child_range(CxxRetainer* self, CxxTimeRange r, CxxTimeRange* tr) {
    auto result = SO_cast<otio::Composition>(self)->trim_child_range(otioTimeRange(r));
    if (result) {
        *tr = cxxTimeRange(*result);
        return true;
    }
    return false;
}

CxxTimeRange composition_range_of_child(CxxRetainer* self, CxxRetainer* child,
                                        CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return cxxTimeRange(SO_cast<otio::Composition>(self)->range_of_child(SO_cast<otio::Composable>(child),
                                                                         &aeh.error_status));
}

bool composition_trimmed_range_of_child(CxxRetainer* self, CxxRetainer* child,
                                        CxxTimeRange* tr, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto result = SO_cast<otio::Composition>(self)->trimmed_range_of_child(SO_cast<otio::Composable>(child),
                                                                           &aeh.error_status);
    if (result) {
        *tr = cxxTimeRange(*result);
        return true;
    }

    return false;
}


// MARK: - MediaReference
bool media_reference_is_missing_reference(CxxRetainer* self) {
    return SO_cast<otio::MediaReference>(self)->is_missing_reference();
}

bool media_reference_available_range(CxxRetainer* self, CxxTimeRange* tr) {
    auto range = SO_cast<otio::MediaReference>(self)->available_range();
    if (range) {
        *tr = cxxTimeRange(*range);
        return true;
    }
    return false;
}

void media_reference_set_available_range(CxxRetainer* self, CxxTimeRange tr) {
    SO_cast<otio::MediaReference>(self)->set_available_range(otioTimeRange(tr));
}

void media_reference_clear_available_range(CxxRetainer* self) {
    SO_cast<otio::MediaReference>(self)->set_available_range(otio::nullopt);
}

// MARK: - Timeline

void* timeline_get_tracks(CxxRetainer* self) {
    return SO_cast<otio::Timeline>(self)->tracks();
}

void timeline_set_tracks(CxxRetainer* self, CxxRetainer* stack) {
    return SO_cast<otio::Timeline>(self)->set_tracks(SO_cast<otio::Stack>(stack));
}

bool timeline_get_global_start_time(CxxRetainer* self, CxxRationalTime* rt) {
    auto gsf = SO_cast<otio::Timeline>(self)->global_start_time();
    if (gsf) {
        *rt = cxxRationalTime(*gsf);
        return true;
    }
    return false;
}

void timeline_set_global_start_time(CxxRetainer* self, CxxRationalTime rt) {
    SO_cast<otio::Timeline>(self)->set_global_start_time(otioRationalTime(rt));
}

void timeline_clear_global_start_time(CxxRetainer* self) {
    SO_cast<otio::Timeline>(self)->set_global_start_time(otio::nullopt);
}

CxxRationalTime timeline_duration(CxxRetainer* self, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return cxxRationalTime(SO_cast<otio::Timeline>(self)->duration(&aeh.error_status));
}

CxxTimeRange timeline_range_of_child(CxxRetainer* self, CxxRetainer* child, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return cxxTimeRange(SO_cast<otio::Timeline>(self)->range_of_child(SO_cast<otio::Composable>(child), &aeh.error_status));
}

NSArray* timeline_audio_tracks(CxxRetainer* self) {
    auto array = [NSMutableArray new];
    for (auto t: SO_cast<otio::Timeline>(self)->audio_tracks()) {
        [array addObject: [NSValue valueWithPointer: t]];
    }
    return array;
}
        
NSArray* timeline_video_tracks(CxxRetainer* self) {
    auto array = [NSMutableArray new];
    for (auto t: SO_cast<otio::Timeline>(self)->video_tracks()) {
        [array addObject: [NSValue valueWithPointer: t]];
    }
    return array;
}

// MARK: - Track
NSString* track_get_kind(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::Track>(self)->kind());
}

void track_set_kind(CxxRetainer* self, NSString* kind) {
    SO_cast<otio::Track>(self)->set_kind([kind UTF8String]);
}

void track_neighbors_of(CxxRetainer* self, CxxRetainer* item, int insert_gap, void** leftNbr, void** rightNbr, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    auto result = SO_cast<otio::Track>(self)->neighbors_of(SO_cast<otio::Composable>(item),
                                                           &aeh.error_status, otio::Track::NeighborGapPolicy(insert_gap));
    *leftNbr = result.first.value;
    *rightNbr = result.second.value;
}

 // MARK: - Effect
NSString* effect_get_name(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::Effect>(self)->name());
}

void effect_set_name(CxxRetainer* self, NSString* name) {
    SO_cast<otio::Effect>(self)->set_name([name UTF8String]);
}

// MARK: - ExternalReference
NSString* external_reference_get_target_url(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::ExternalReference>(self)->target_url());
}
 
void external_reference_set_target_url(CxxRetainer* self, NSString* target_url) {
    SO_cast<otio::ExternalReference>(self)->set_target_url([target_url UTF8String]);
}

// MARK: - GeneratorReference
NSString* generator_reference_get_generator_kind(CxxRetainer* self) {
    return make_nsstring(SO_cast<otio::GeneratorReference>(self)->generator_kind());
}

void generator_reference_set_generator_kind(CxxRetainer* self, NSString* kind) {
    SO_cast<otio::GeneratorReference>(self)->set_generator_kind([kind UTF8String]);
}
 
void* generator_reference_parameters(CxxRetainer* self) {
    return &SO_cast<otio::GeneratorReference>(self)->parameters();
}

// MARK: - LinearTimeWarp
double linear_time_warp_get_time_scalar(CxxRetainer* self) {
    return SO_cast<otio::LinearTimeWarp>(self)->time_scalar();
}
 
void linear_time_warp_set_time_scalar(CxxRetainer* self, double time_scalar) {
    SO_cast<otio::LinearTimeWarp>(self)->set_time_scalar(time_scalar);
}

// MARK: - Algorithms
void* algorithms_track_trimmed_to_range(CxxRetainer* in_track, CxxTimeRange trim_range,
                                        CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return otio::track_trimmed_to_range(SO_cast<otio::Track>(in_track),
                                        otioTimeRange(trim_range), &aeh.error_status);
}

void* algorithms_flatten_stack(CxxRetainer* in_stack, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    return otio::flatten_stack(SO_cast<otio::Stack>(in_stack), &aeh.error_status);    
}

void* algorithms_flatten_track_array(NSArray* tracks, CxxErrorStruct* cxxErr) {
    _AutoErrorHandler aeh(cxxErr);
    std::vector<otio::Track*> trackVector;
    trackVector.reserve([tracks count]);

    for (CxxRetainer* e: tracks) {
        trackVector.push_back(SO_cast<otio::Track>(e));
    }
    return otio::flatten_stack(trackVector, &aeh.error_status);
}
