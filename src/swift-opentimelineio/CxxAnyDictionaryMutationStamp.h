//
//  CxxAnyDictionary.h
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import <Foundation/Foundation.h>
#import "opentime.h"

#if defined(__cplusplus)
#import <opentimelineio/anyDictionary.h>
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
#endif

NS_ASSUME_NONNULL_BEGIN

@interface CxxAnyDictionaryMutationStamp : NSObject
- (instancetype) init:(void*) anyDictionaryPtr;

- (bool) lookup:(NSString*) key
          asInt: (int*) result;

- (bool) lookup:(NSString*) key
 asRationalTime:(CxxRationalTime*) result;

- (CxxAnyDictionaryMutationStamp* _Nullable_) lookupAsDictionary:(NSString*) key;
@end

#if defined(__cplusplus)
@interface CxxAnyDictionaryMutationStamp ()
@property otio::AnyDictionary::MutationStamp* mutationStamp;
@end

#endif

NS_ASSUME_NONNULL_END
