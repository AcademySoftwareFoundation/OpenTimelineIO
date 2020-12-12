//
//  CxxAnyVector.h
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import <Foundation/Foundation.h>
#import "opentime.h"
#import "CxxRetainer.h"
#import "CxxAny.h"

#if defined(__cplusplus)
#import <opentimelineio/anyVector.h>
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
#endif

NS_ASSUME_NONNULL_BEGIN

@interface CxxAnyVectorMutationStamp : NSObject
- (instancetype) init:(void* _Nullable) anyVectorPtr;
- (void*) cxxAnyVectorPtr;
- (bool) lookup:(int) index
         result:(CxxAny*) ptr;
- (void) store:(int) index
         value:(CxxAny) cxxAny;
- (void) moveIndex:(int) fromIndex
         toIndex:(int) toIndex;
- (void) addAtEnd:(CxxAny) cxxAny;
- (void) shrinkOrGrow:(int) n
                 grow:(bool) grow;
- (void) setContents:(CxxAnyVectorMutationStamp*) src
       destroyingSrc:(bool) destroyingSrc;
- (int) count;
@end

#if defined(__cplusplus)
@interface CxxAnyVectorMutationStamp ()
@property otio::AnyVector::MutationStamp* mutationStamp;
 @end

#endif

NS_ASSUME_NONNULL_END
