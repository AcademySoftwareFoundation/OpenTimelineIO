//
//  CxxAnyDictionary.h
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import <Foundation/Foundation.h>
#import "opentime.h"
#import "CxxRetainer.h"
#import "CxxAny.h"

#if defined(__cplusplus)
#import <opentimelineio/anyDictionary.h>
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
#endif

NS_ASSUME_NONNULL_BEGIN

@interface CxxAnyDictionaryMutationStamp : NSObject
- (instancetype) init:(void* _Nullable) anyDictionaryPtr
          cxxRetainer:(CxxRetainer* _Nullable) owner;
- (void*) cxxAnyDictionaryPtr;
- (bool) lookup:(NSString*) key
         result:(CxxAny*) ptr;
- (void) store:(NSString*) key
           value:(CxxAny) cxxAny;
- (void) setContents:(CxxAnyDictionaryMutationStamp*) src
       destroyingSrc:(bool) destroyingSrc;
- (void) removeValue:(NSString*) key;
- (int) count;

@property CxxRetainer* owner;
@end

#if defined(__cplusplus)
@interface CxxAnyDictionaryMutationStamp ()
@property otio::AnyDictionary::MutationStamp* mutationStamp;
 @end

#endif

NS_ASSUME_NONNULL_END
