//
//  opentimelineio.h
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>
#import "CxxRetainer.h"
#import "CxxAnyDictionaryMutationStamp.h"
#import "errorStruct.h"

#if defined(__cplusplus)
extern "C" {
#endif
    
NS_ASSUME_NONNULL_BEGIN
    
CxxRetainer* new_clip();
CxxRetainer* new_composable();
CxxRetainer* new_composition();
CxxRetainer* new_effect();
CxxRetainer* new_external_reference();
CxxRetainer* new_freeze_frame();
CxxRetainer* new_gap();
CxxRetainer* new_generator_reference();
CxxRetainer* new_item();
CxxRetainer* new_linear_time_warp();
CxxRetainer* new_marker();
CxxRetainer* new_media_reference();
CxxRetainer* new_missing_reference();
CxxRetainer* new_serializable_collection();
CxxRetainer* new_serializable_object();
CxxRetainer* new_serializable_object_with_metadata();
CxxRetainer* new_stack();
CxxRetainer* new_time_effect();
CxxRetainer* new_timeline();
CxxRetainer* new_track();
CxxRetainer* new_transition();
    
// SerializableObject
    
void serializable_object_to_json_file(CxxRetainer*, NSString* filename, int indent, CxxErrorStruct* err);
NSString* serializable_object_to_json_string(CxxRetainer*, int indent, CxxErrorStruct* err);
    
void* serializable_object_from_json_string(NSString* input, CxxErrorStruct* cxxErr);
void* serializable_object_from_json_file(NSString* filename, CxxErrorStruct* cxxErr);
void* serializable_object_clone(CxxRetainer* r, CxxErrorStruct* cxxErr);

NSString* serializable_object_schema_name(CxxRetainer*);
int serializable_object_schema_version(CxxRetainer*);
NSString* serializable_object_to_json(CxxRetainer*, CxxErrorStruct* err);
    
bool serializable_object_is_equivalent_to(CxxRetainer*, CxxRetainer*);
void* clone(CxxRetainer*, CxxErrorStruct* err);
    
bool serializable_object_is_unknown_schema(CxxRetainer*);
    
// SerializableObjectWithMetadata
    
NSString* serializable_object_with_metadata_name(CxxRetainer*);
void serializable_object_with_metadata_set_name(CxxRetainer*, NSString* name);

    
NS_ASSUME_NONNULL_END
    
#if defined(__cplusplus)
}
#endif
