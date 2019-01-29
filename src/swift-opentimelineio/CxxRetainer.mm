//
//  CxxRetainer.m
//  otio_macos
//
//  Created by David Baraff on 1/17/19.
//

#import "CxxRetainer.h"

@implementation CxxRetainer
- (instancetype) init:(void*) cxxPtr {
    if ((self = [super init])) {
        otio::SerializableObject* so = reinterpret_cast<otio::SerializableObject*>(cxxPtr);
        self.retainer = otio::SerializableObject::Retainer<>(so);
    }
    
    return self;
}
- (void*) cxxSerializableObject {
    return self.retainer.value;
}
@end
