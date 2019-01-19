//
//  CxxRetainer.m
//  otio_macos
//
//  Created by David Baraff on 1/17/19.
//

#import "CxxRetainer.h"

@implementation CxxRetainer
- (void*) cxxSerializableObject {
    return self.retainer.value;
}
@end
