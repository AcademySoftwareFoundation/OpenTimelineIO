//
//  opentimelineio.h
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>
#import "CxxRetainer.h"
#import "CxxAnyDictionaryMutationStamp.h"
#import "CxxAnyDictionaryIterator.h"
#import "CxxAnyVectorMutationStamp.h"
#import "CxxVectorProperty.h"
#import "errorStruct.h"

#if defined(__cplusplus)
extern "C" {
#endif
    
NS_ASSUME_NONNULL_BEGIN
    

// MARK: otio_new_XXX methods
    
void* otio_new_clip();
void* otio_new_composable();
void* otio_new_composition();
void* otio_new_effect();
void* otio_new_external_reference();
void* otio_new_freeze_frame();
void* otio_new_gap();
void* otio_new_generator_reference();
void* otio_new_item();
void* otio_new_linear_time_warp();
void* otio_new_marker();
void* otio_new_media_reference();
void* otio_new_missing_reference();
void* otio_new_serializable_collection();
void* otio_new_serializable_object();
void* otio_new_serializable_object_with_metadata();
void* otio_new_stack();
void* otio_new_time_effect();
void* otio_new_timeline();
void* otio_new_track();
void* otio_new_transition();

// MARK: SerializableObject
    
void serializable_object_to_json_file(CxxRetainer* self, NSString* filename, int indent, CxxErrorStruct* err);
NSString* serializable_object_to_json_string(CxxRetainer* self, int indent, CxxErrorStruct* err);
    
void* serializable_object_from_json_string(NSString* input, CxxErrorStruct* cxxErr);
void* serializable_object_from_json_file(NSString* filename, CxxErrorStruct* cxxErr);
void* serializable_object_clone(CxxRetainer* r, CxxErrorStruct* cxxErr);

NSString* serializable_object_schema_name_from_ptr(void* cxxPtr);
NSString* serializable_object_schema_name(CxxRetainer* self);
int serializable_object_schema_version(CxxRetainer* self);
    
NSString* serializable_object_to_json(CxxRetainer* self, CxxErrorStruct* err);
bool serializable_object_is_equivalent_to(CxxRetainer* self, CxxRetainer*);
void* clone(CxxRetainer* self, CxxErrorStruct* err);
    
bool serializable_object_is_unknown_schema(CxxRetainer* self);
    
// MARK: SerializableObject.Vector
void serializable_object_new_serializable_object_vector(CxxVectorProperty* p);
void serializable_object_new_marker_vector(CxxVectorProperty* p);
void serializable_object_new_effect_vector(CxxVectorProperty* p);

// MARK: - SerializableObject.Vector
    
void serializable_object_new_serializable_object_vector(CxxVectorProperty* p);
void serializable_object_new_marker_vector(CxxVectorProperty* p);
void serializable_object_new_effect_vector(CxxVectorProperty* p);
    
// MARK: - UnknownSchema

NSString* unknown_schema_original_schema_name(CxxRetainer* self);
int unknown_schema_original_schema_version(CxxRetainer* self);

// MARK: - SerializableObjectWithMetadata
    
NSString* serializable_object_with_metadata_name(CxxRetainer* self);
void serializable_object_with_metadata_set_name(CxxRetainer* self, NSString* name);
void* serializable_object_with_metadata_metadata(CxxRetainer* self);
    
// MARK: - Clip
void* _Nullable clip_media_reference(CxxRetainer* self);
void clip_set_media_reference(CxxRetainer* self, CxxRetainer* _Nullable media_reference);
    
// MARK: - Effect
NSString* effect_get_name(CxxRetainer* self);
void effect_set_name(CxxRetainer* self, NSString*);

// MARK: - ExternalReference
NSString* external_reference_get_target_url(CxxRetainer* self);
void external_reference_set_target_url(CxxRetainer* self, NSString*);

// MARK: - GeneratorReference
NSString* generator_reference_get_generator_kind(CxxRetainer* self);
void generator_reference_set_generator_kind(CxxRetainer* self, NSString*);
void* generator_reference_parameters(CxxRetainer* self);

// MARK: - LinearTimeWarp
double linear_time_warp_get_time_scalar(CxxRetainer* self);
void linear_time_warp_set_time_scalar(CxxRetainer* self, double time_scalar);

// MARK: - Composable
void* _Nullable composable_parent(CxxRetainer* self);
bool composable_visible(CxxRetainer* self);
bool composable_overlapping(CxxRetainer* self);
CxxRationalTime composable_duration(CxxRetainer* self, CxxErrorStruct*);
    
// MARK: - Marker
NSString* marker_get_color(CxxRetainer* self);
void marker_set_color(CxxRetainer* self, NSString*);
CxxTimeRange marker_get_marked_range(CxxRetainer* self);
void marker_set_marked_range(CxxRetainer* self, CxxTimeRange);

// MARK: - SerializableCollection
CxxVectorProperty* create_serializable_collection_children_vector_property(CxxRetainer* self);
           
// MARK: - Item
CxxVectorProperty* create_item_markers_vector_property(CxxRetainer* self);
CxxVectorProperty* create_item_effects_vector_property(CxxRetainer* self);
bool item_get_source_range(CxxRetainer* self, CxxTimeRange*);
void item_set_source_range(CxxRetainer* self, CxxTimeRange);
void item_set_source_range_to_null(CxxRetainer* self);
CxxTimeRange item_available_range(CxxRetainer* self, CxxErrorStruct*);
CxxTimeRange item_trimmed_range(CxxRetainer* self, CxxErrorStruct*);
CxxTimeRange item_visible_range(CxxRetainer* self, CxxErrorStruct*);
bool item_trimmed_range_in_parent(CxxRetainer* self, CxxTimeRange*, CxxErrorStruct*);
CxxTimeRange item_range_in_parent(CxxRetainer* self, CxxErrorStruct*);
CxxRationalTime item_transformed_time(CxxRetainer* self, CxxRationalTime, CxxRetainer* to_item, CxxErrorStruct*);
CxxTimeRange item_transformed_time_range(CxxRetainer* self, CxxTimeRange, CxxRetainer* to_item, CxxErrorStruct*);

// MARK: - Transition
CxxRationalTime transition_get_in_offset(CxxRetainer* self);
void transition_set_in_offset(CxxRetainer* self, CxxRationalTime);
   
CxxRationalTime transition_get_out_offset(CxxRetainer* self);
void transition_set_out_offset(CxxRetainer* self, CxxRationalTime);
    
NSString* transition_get_transition_type(CxxRetainer* self);
void transition_set_transition_type(CxxRetainer* self, NSString*);

bool transition_range_in_parent(CxxRetainer* self, CxxTimeRange* tr, CxxErrorStruct* cxxErr);
bool transition_trimmed_range_in_parent(CxxRetainer* self, CxxTimeRange* tr, CxxErrorStruct* cxxErr);

// MARK: - Composition
CxxVectorProperty* create_composition_children_vector_property(CxxRetainer* self);
    
void composition_remove_all_children(CxxRetainer* self);
void composition_replace_child(CxxRetainer* self, int index, CxxRetainer* child, CxxErrorStruct*);
void composition_insert_child(CxxRetainer* self, int index, CxxRetainer* child, CxxErrorStruct*);
void composition_remove_child(CxxRetainer* self, int index, CxxErrorStruct*);
void composition_append_child(CxxRetainer* self, CxxRetainer* child, CxxErrorStruct*);
NSDictionary* composition_range_of_all_children(CxxRetainer* self, CxxErrorStruct*);
NSString* composition_composition_kind(CxxRetainer* self);
bool composition_is_parent_of(CxxRetainer* self, CxxRetainer* composable);
bool composition_has_child(CxxRetainer* self, CxxRetainer* composable);
void composition_handles_of_child(CxxRetainer* self, CxxRetainer* composable,
                                 CxxRationalTime* rt1, CxxRationalTime* rt2,
                                 bool* hasLeft, bool* hasRight, CxxErrorStruct* cxxErr);
CxxTimeRange composition_range_of_child_at_index(CxxRetainer* self, int index,
                                        CxxErrorStruct* cxxErr);
CxxTimeRange composition_trimmed_range_of_child_at_index(CxxRetainer* self, int index,
                                        CxxErrorStruct* cxxErr);
bool composition_trim_child_range(CxxRetainer* self, CxxTimeRange r, CxxTimeRange* tr);

CxxTimeRange composition_range_of_child(CxxRetainer* self, CxxRetainer* child,
                                        CxxErrorStruct* cxxErr);

bool composition_trimmed_range_of_child(CxxRetainer* self, CxxRetainer* child,
                                        CxxTimeRange* tr, CxxErrorStruct* cxxErr);

// MARK: - MediaReference
bool media_reference_is_missing_reference(CxxRetainer* self);
bool media_reference_available_range(CxxRetainer* self, CxxTimeRange*);
void media_reference_set_available_range(CxxRetainer* self, CxxTimeRange);
void media_reference_clear_available_range(CxxRetainer* self);
    
// MARK: - Timeline
void* timeline_get_tracks(CxxRetainer* self);    
void timeline_set_tracks(CxxRetainer* self, CxxRetainer* stack);

bool timeline_get_global_start_time(CxxRetainer* self, CxxRationalTime*);
void timeline_set_global_start_time(CxxRetainer* self, CxxRationalTime);
void timeline_clear_global_start_time(CxxRetainer* self);

CxxRationalTime timeline_duration(CxxRetainer* self, CxxErrorStruct* cxxErr);    
CxxTimeRange timeline_range_of_child(CxxRetainer* self, CxxRetainer* child, CxxErrorStruct* cxxErr);

NSArray* timeline_audio_tracks(CxxRetainer* self);
NSArray* timeline_video_tracks(CxxRetainer* self);

// MARK: - Track
NSString* track_get_kind(CxxRetainer* self);
void track_set_kind(CxxRetainer* self, NSString*);
void track_neighbors_of(CxxRetainer* self, CxxRetainer* item,
                        int insert_gap,
                        void* _Nullable * _Nonnull leftNbr,
                        void* _Nullable * _Nonnull rightNbr,
                        CxxErrorStruct* cxxErr);
    
// MARK: - Algorithms
void* algorithms_track_trimmed_to_range(CxxRetainer* in_track, CxxTimeRange trim_range,
                                        CxxErrorStruct* cxxErr);
void* algorithms_flatten_stack(CxxRetainer* in_stack, CxxErrorStruct* cxxErr);
void* algorithms_flatten_track_array(NSArray* tracks, CxxErrorStruct* cxxErr);    
    
NS_ASSUME_NONNULL_END

#if defined(__cplusplus)
}
#endif
