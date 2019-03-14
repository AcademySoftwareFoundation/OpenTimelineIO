//
//  CxxVectorProperty.m
//  otio_macos
//
//  Created by David Baraff on 3/1/19.
//

#import "CxxVectorProperty.h"

CxxSOVectorBase::CxxSOVectorBase() {
}

CxxSOVectorBase::~CxxSOVectorBase() {
}

@implementation CxxVectorProperty
- (instancetype) init {
    self = [super init];
    self.cxxVectorBase = nullptr;
    return self;
}

- (void) dealloc {
    delete self.cxxVectorBase;
}

- (int) count {
    return self.cxxVectorBase->size();
}

- (void) clear {
    self.cxxVectorBase->clear();
}

- (void*) cxxSerializableObjectAtIndex:(int) index {
    return self.cxxVectorBase->fetch(index);
}

- (void) store:(int) index
         value:(void*) cxxSerializableObject {
    self.cxxVectorBase->store(index, (otio::SerializableObject*)cxxSerializableObject);
}

- (void) moveIndex:(int) fromIndex
           toIndex:(int) toIndex {
    self.cxxVectorBase->moveIndex(fromIndex, toIndex);
}

- (void) addAtEnd:(void*) cxxSerializableObject {
    self.cxxVectorBase->append((otio::SerializableObject*)cxxSerializableObject);
}

- (void) shrinkOrGrow:(int) n
                 grow:(bool) grow {
    self.cxxVectorBase->shrinkOrGrow(n, grow);
}

- (void) removeAtEnd {
    self.cxxVectorBase->removeAtEnd();
}

- (void) copyContents:(CxxVectorProperty*) src {
    if (src.cxxVectorBase != self.cxxVectorBase) {
        self.cxxVectorBase->setContents(src->_cxxVectorBase, false /* destroyingSrc */);
    }
}

- (void) moveContents:(CxxVectorProperty*) src {
    if (src.cxxVectorBase != self.cxxVectorBase) {
        self.cxxVectorBase->setContents(src->_cxxVectorBase, true /* destroyingSrc */);
    }
}

@end
