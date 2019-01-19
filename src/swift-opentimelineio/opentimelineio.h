//
//  opentimelineio.h
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>
#import "CxxRetainer.h"

#if defined(__cplusplus)
extern "C" {
#endif

CxxRetainer* _Nonnull new_serializable_object();
CxxRetainer* _Nonnull new_serializable_object_with_metadata(void*);
    
NSString* serializable_object_schema_name(CxxRetainer* _Nonnull);
NSString* serializable_object_to_json(CxxRetainer* _Nonnull);
    
NSString* serializable_object_with_metadata_name(CxxRetainer* _Nonnull );
void serializable_object_with_metadata_set_name(CxxRetainer* _Nonnull, NSString* name);

void* _Nonnull  serializable_object_special_object();
    
#if defined(__cplusplus)
}
#endif
