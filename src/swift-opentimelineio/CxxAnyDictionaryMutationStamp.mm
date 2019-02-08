//
//  CxxAnyDictionary.m
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import "CxxAnyDictionaryMutationStamp.h"

struct DerivedMutationStamp : public otio::AnyDictionary::MutationStamp {
    
};

@implementation CxxAnyDictionaryMutationStamp

- (instancetype) init:(void*) anyDictionaryPtr {
    if ((self = [super init])) {
        if (anyDictionaryPtr) {
            otio::AnyDictionary* d = reinterpret_cast<otio::AnyDictionary*>(anyDictionaryPtr);
            self.mutationStamp = d->get_or_create_mutation_stamp();
        }
        else {
            self.mutationStamp = new DerivedMutationStamp;
        }
    }
    
    return self;
}

- (void) dealloc {
    if (self.mutationStamp->owning) {
        delete self.mutationStamp;
    }
}

- (bool) lookup:(NSString*) key
          asInt: (int*) result {
    if (auto dict = self.mutationStamp->any_dictionary) {
        auto it = dict->find(std::string(key.UTF8String));
        if (it != dict->end()) {
            if ((*it)->
        }

    }
    
    if (self.mutationStamp->any_dictionary) {
        auto result = self.mutationStamp->any_dictionary
}

- (bool) lookup:(NSString*) key
 asRationalTime:(CxxRationalTime*) result;

- (CxxAnyDictionaryMutationStamp* _Nullable_) lookupAsDictionary:(NSString*) key;

@end
