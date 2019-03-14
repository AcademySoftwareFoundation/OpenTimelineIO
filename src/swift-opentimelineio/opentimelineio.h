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
    
void serializable_object_to_json_file(CxxRetainer*, NSString* filename, int indent, CxxErrorStruct* err);
NSString* serializable_object_to_json_string(CxxRetainer*, int indent, CxxErrorStruct* err);
    
void* serializable_object_from_json_string(NSString* input, CxxErrorStruct* cxxErr);
void* serializable_object_from_json_file(NSString* filename, CxxErrorStruct* cxxErr);
void* serializable_object_clone(CxxRetainer* r, CxxErrorStruct* cxxErr);

NSString* serializable_object_schema_name_from_ptr(void* cxxPtr);
NSString* serializable_object_schema_name(CxxRetainer*);
int serializable_object_schema_version(CxxRetainer*);
    
NSString* serializable_object_to_json(CxxRetainer*, CxxErrorStruct* err);
bool serializable_object_is_equivalent_to(CxxRetainer*, CxxRetainer*);
void* clone(CxxRetainer*, CxxErrorStruct* err);
    
bool serializable_object_is_unknown_schema(CxxRetainer*);
    
// MARK: SerializableObject.Vector
void serializable_object_new_serializable_object_vector(CxxVectorProperty* p);
void serializable_object_new_marker_vector(CxxVectorProperty* p);
void serializable_object_new_effect_vector(CxxVectorProperty* p);

// MARK: - SerializableObject.Vector
    
void serializable_object_new_serializable_object_vector(CxxVectorProperty* p);
void serializable_object_new_marker_vector(CxxVectorProperty* p);
void serializable_object_new_effect_vector(CxxVectorProperty* p);
    
// MARK: - UnknownSchema

NSString* unknown_schema_original_schema_name(CxxRetainer*);
int unknown_schema_original_schema_version(CxxRetainer*);

// MARK: - SerializableObjectWithMetadata
    
NSString* serializable_object_with_metadata_name(CxxRetainer*);
void serializable_object_with_metadata_set_name(CxxRetainer*, NSString* name);
void* serializable_object_with_metadata_metadata(CxxRetainer* r);
    
// MARK: - Composable
void* composable_parent(CxxRetainer*);
bool composable_visible(CxxRetainer*);
bool composable_overlapping(CxxRetainer*);

// MARK: - Marker
NSString* marker_get_color(CxxRetainer*);
void marker_set_color(CxxRetainer*, NSString*);
CxxTimeRange marker_get_marked_range(CxxRetainer*);
void marker_set_marked_range(CxxRetainer*, CxxTimeRange);

// MARK: - Composition
CxxVectorProperty* create_composition_children_vector_property(CxxRetainer* copmosition_retainer);
    
// MARK: - SerializableCollection
CxxVectorProperty* create_serializable_collection_children_vector_property(CxxRetainer* sc_retainer);
           
// MARK: - Item
CxxVectorProperty* create_item_markers_vector_property(CxxRetainer* item_retainer);
CxxVectorProperty* create_item_effects_vector_property(CxxRetainer* item_retainer);
bool item_get_source_range(CxxRetainer*, CxxTimeRange*);
void item_set_source_range(CxxRetainer*, CxxTimeRange);
void item_set_source_range_to_null(CxxRetainer*);
CxxRationalTime item_duration(CxxRetainer* item_retainer, CxxErrorStruct*);
CxxTimeRange item_available_range(CxxRetainer* item_retainer, CxxErrorStruct*);
CxxTimeRange item_trimmed_range(CxxRetainer* item_retainer, CxxErrorStruct*);
CxxTimeRange item_visible_range(CxxRetainer* item_retainer, CxxErrorStruct*);
bool item_trimmed_range_in_parent(CxxRetainer* item_retainer, CxxTimeRange*, CxxErrorStruct*);
CxxTimeRange item_range_in_parent(CxxRetainer* item_retainer, CxxErrorStruct*);
CxxRationalTime item_transformed_time(CxxRetainer* item_retainer, CxxRationalTime, CxxRetainer* to_item, CxxErrorStruct*);
CxxTimeRange item_transformed_time_range(CxxRetainer* item_retainer, CxxTimeRange, CxxRetainer* to_item, CxxErrorStruct*);

    
NS_ASSUME_NONNULL_END
    
#if defined(__cplusplus)
}
#endif
