//
//  CxxAnyDictionary.m
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import "CxxAnyDictionaryMutationStamp.h"

namespace {
    struct DerivedMutationStamp : public otio::AnyDictionary::MutationStamp {
    
    };
}

template <typename T>
static bool lookup(otio::AnyDictionary::MutationStamp* mutationStamp, NSString* key, T* result) {
    if (auto dict = mutationStamp->any_dictionary) {
        auto it = dict->find(std::string(key.UTF8String));
        if (it != dict->end()) {
            if (it->second.type() == typeid(T)) {
                *result = otio::any_cast<T>(it->second);
                return true;
            }
        }
    }
    return false;
}

@implementation CxxAnyDictionaryMutationStamp

- (instancetype) init:(void*) anyDictionaryPtr
          cxxRetainer:(CxxRetainer*) owner {
    if ((self = [super init])) {
        if (anyDictionaryPtr) {
            otio::AnyDictionary* d = reinterpret_cast<otio::AnyDictionary*>(anyDictionaryPtr);
            self.mutationStamp = d->get_or_create_mutation_stamp();
        }
        else {
            self.mutationStamp = new DerivedMutationStamp;
        }
        self.owner = owner;
    }
    
    return self;
}

- (void) dealloc {
    if (self.mutationStamp->owning) {
        delete self.mutationStamp;
    }
}

- (void*) cxxAnyDictionaryPtr {
    return self.mutationStamp->any_dictionary;
}

- (bool) lookup:(NSString*) key
         result:(CxxAny*) cxxAny {
    if (auto dict = self.mutationStamp->any_dictionary) {
        auto it = dict->find(std::string(key.UTF8String));
        if (it != dict->end()) {
            otio_any_to_cxx_any(it->second, cxxAny);
            return true;
        }
    }
    return false;
}

- (void) store:(NSString*) key
           value:(CxxAny) cxxAny {
    if (auto dict = self.mutationStamp->any_dictionary) {
        auto skey = std::string(key.UTF8String);
        auto it = dict->find(skey);
        if (it != dict->end()) {
            otio::any a = cxx_any_to_otio_any(cxxAny);
            std::swap(it->second, a);
        }
        else {
            dict->emplace(skey, cxx_any_to_otio_any(cxxAny));
        }
    }
}

- (void) setContents:(CxxAnyDictionaryMutationStamp*) src
       destroyingSrc:(bool) destroyingSrc {
    if (auto d = self.mutationStamp->any_dictionary) {
        if (auto dSrc = src.mutationStamp->any_dictionary) {
            if (destroyingSrc) {
                d->swap(*dSrc);
            }
            else {
                *d = *dSrc;
            }
        }
    }
}

- (void) removeValue:(NSString*) key {
    if (auto dict = self.mutationStamp->any_dictionary) {
        auto skey = std::string(key.UTF8String);
        dict->erase(skey);
    }
}

- (int) count {
    if (auto dict = self.mutationStamp->any_dictionary) {
        return int(dict->size());
    }
    else {
        return 0;
    }
}

@end
