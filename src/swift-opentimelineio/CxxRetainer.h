//
//  CxxRetainer.h
//  otio_macos
//
//  Created by David Baraff on 1/17/19.
//

#import <Foundation/Foundation.h>

#if defined(__cplusplus)
#import <opentimelineio/serializableObject.h>
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
#endif

NS_ASSUME_NONNULL_BEGIN

@interface CxxRetainer : NSObject
- (void*) cxxSerializableObject;
@end

#if defined(__cplusplus)
@interface CxxRetainer ()
@property otio::SerializableObject::Retainer<> retainer;
@end

template <typename T = otio::SerializableObject>
inline T* _Nonnull serializableObject(CxxRetainer const* r) {
    return (T*) r.retainer.value;
}

#endif

NS_ASSUME_NONNULL_END
