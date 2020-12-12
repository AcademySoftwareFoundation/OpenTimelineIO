//
//  CxxAnyDictionary.h
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import <Foundation/Foundation.h>
#import "opentime.h"
#import "CxxAnyDictionaryMutationStamp.h"

NS_ASSUME_NONNULL_BEGIN

@interface CxxAnyDictionaryIterator : NSObject
- (instancetype) init:(CxxAnyDictionaryMutationStamp*) cxxAnyDictionaryMutationStamp;
@property CxxAnyDictionaryMutationStamp* cxxAnyDictionaryMutationStamp;
@property int64_t startingStamp;

- (NSString* _Nullable) nextElement:(CxxAny*) cxxAny;
- (NSString* _Nullable) currentElement:(CxxAny*) cxxAny;
- (void) jumpToEnd;
- (void) jumpToIndexAfter:(CxxAnyDictionaryIterator*) cxxAnyDictionaryIterator;
- (bool) lessThan:(CxxAnyDictionaryIterator*) rhs;
- (bool) equal:(CxxAnyDictionaryIterator*) rhs;
- (int) distanceTo:(CxxAnyDictionaryIterator*) rhs;
- (void) store:(CxxAny) cxxAny;
@end

#if defined(__cplusplus)
@interface CxxAnyDictionaryIterator ()
@property otio::AnyDictionary::iterator iterator;
@property int position;
@end

#endif

NS_ASSUME_NONNULL_END
