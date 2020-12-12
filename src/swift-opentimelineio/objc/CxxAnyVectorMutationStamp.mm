//
//  CxxAnyVector.m
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import "CxxAnyVectorMutationStamp.h"

namespace {
    struct DerivedMutationStamp : public otio::AnyVector::MutationStamp {
    
    };
}

template <typename T>
static bool lookup(otio::AnyVector::MutationStamp* mutationStamp, int index, T* result) {
    if (auto v = mutationStamp->any_vector) {
        if (index < v->size()) {
            if ((*v)[index].type() == typeid(T)) {
                *result = otio::any_cast<T>(v[index]);
                return true;
            }
        }
    }
    return false;
}

@implementation CxxAnyVectorMutationStamp

- (instancetype) init:(void*) anyVectorPtr {
    if ((self = [super init])) {
        if (anyVectorPtr) {
            otio::AnyVector* v = reinterpret_cast<otio::AnyVector*>(anyVectorPtr);
            self.mutationStamp = v->get_or_create_mutation_stamp();
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

- (void*) cxxAnyVectorPtr {
    return self.mutationStamp->any_vector;
}

- (bool) lookup:(int) index
         result:(CxxAny*) cxxAny {
    if (auto v = self.mutationStamp->any_vector) {
        if (index >= 0 && index < v->size()) {
            otio_any_to_cxx_any((*v)[index], cxxAny);
            return true;
        }
    }
    return false;
}

- (void) store:(int) index
           value:(CxxAny) cxxAny {
    if (auto v = self.mutationStamp->any_vector) {
        if (index >= 0 && index < v->size()) {
            otio::any a = cxx_any_to_otio_any(cxxAny);
            std::swap((*v)[index], a);
        }
        else {
            v->emplace_back(cxx_any_to_otio_any(cxxAny));
        }
    }
}

- (void) moveIndex:(int) fromIndex
           toIndex:(int) toIndex {
    if (auto v = self.mutationStamp->any_vector) {
        (*v)[toIndex].swap((*v)[fromIndex]);
    }
}

- (void) addAtEnd:(CxxAny) cxxAny {
    if (auto v = self.mutationStamp->any_vector) {
        v->emplace_back(cxx_any_to_otio_any(cxxAny));
    }
}

- (void) shrinkOrGrow:(int) n
                 grow:(bool) grow {
    if (auto v = self.mutationStamp->any_vector) {
        if (grow) {
            for (int i = 0; i < n; i++) {
                v->push_back(otio::any());
            }
        }
        else {
            if (n >= v->size()) {
                v->clear();
                return;
            }

            for (int i = 0; i < n; i++) {
                    v->pop_back();
            }
        }
    }
}

- (void) removeAtEnd {
    if (auto v = self.mutationStamp->any_vector) {
        if (!v->empty()) {
            v->pop_back();
        }
    }
}

- (void) setContents:(CxxAnyVectorMutationStamp*) src
       destroyingSrc:(bool) destroyingSrc {
    if (auto v = self.mutationStamp->any_vector) {
        if (auto vSrc = src.mutationStamp->any_vector) {
            if (destroyingSrc) {
                v->swap(*vSrc);
            }
            else {
                *v = *vSrc;
            }
        }
    }
}

- (int) count {
    if (auto v = self.mutationStamp->any_vector) {
        return int(v->size());
    }
    else {
        return 0;
    }
}

@end
