//
//  CxxAnyDictionary.m
//  otio_macos
//
//  Created by David Baraff on 1/31/19.
//

#import "CxxAnyDictionaryIterator.h"

template <typename T>
static bool lookup(CxxAnyDictionaryIterator* dictionaryIterator, T* result) {
    auto ms = dictionaryIterator.cxxAnyDictionaryMutationStamp.mutationStamp;
    if (ms->stamp != dictionaryIterator.startingStamp) {
        if (auto dict = ms->any_dictionary) {
            if (dictionaryIterator.iterator != dict->end()) {
                if (dictionaryIterator.iterator->second.type() == typeid(T)) {
                    *result = otio::any_cast<T>(dictionaryIterator.iterator->second);
                    return true;
                }
            }
        }
    }
    return false;
}

@implementation CxxAnyDictionaryIterator

- (instancetype) init:(CxxAnyDictionaryMutationStamp*) cxxAnyDictionaryMutationStamp {
    if ((self = [super init])) {
        self.cxxAnyDictionaryMutationStamp = cxxAnyDictionaryMutationStamp;
        auto ms = cxxAnyDictionaryMutationStamp.mutationStamp;
        self.startingStamp = ms->stamp;
        if (ms->any_dictionary) {
            self.iterator = ms->any_dictionary->begin();
            self.position = 0;
        }
    }
    
    return self;
}

- (NSString* _Nullable) currentElement:(CxxAny*) cxxAny {
    auto ms = self.cxxAnyDictionaryMutationStamp.mutationStamp;
    if (ms->stamp == self.startingStamp) {
        if (auto dict = ms->any_dictionary) {
            if (self.iterator != dict->end()) {
                otio_any_to_cxx_any(self.iterator->second, cxxAny);
                auto key = [NSString stringWithUTF8String: self.iterator->first.c_str()];
                return key;
            }
        }
    }
    
    return nil;
}

- (NSString* _Nullable) nextElement:(CxxAny*) cxxAny {
    auto ms = self.cxxAnyDictionaryMutationStamp.mutationStamp;
    if (ms->stamp == self.startingStamp) {
        if (auto dict = ms->any_dictionary) {
            if (self.iterator != dict->end()) {
                otio_any_to_cxx_any(self.iterator->second, cxxAny);
                auto key = [NSString stringWithUTF8String: self.iterator->first.c_str()];
                ++self->_iterator;
                ++self->_position;
                return key;
            }
        }
    }
    
    return nil;
}

- (void) jumpToEnd {
    auto ms = self.cxxAnyDictionaryMutationStamp.mutationStamp;
    if (auto dict = ms->any_dictionary) {
        self.iterator = dict->end();
        self.position = int(dict->size());
    }
}

- (void) jumpToIndexAfter:(CxxAnyDictionaryIterator*) cxxAnyDictionaryIterator {
    self.iterator = cxxAnyDictionaryIterator.iterator;
    self.position = cxxAnyDictionaryIterator.position + 1;
    ++self->_iterator;
}

- (void) store:(CxxAny) cxxAny {
    auto ms = self.cxxAnyDictionaryMutationStamp.mutationStamp;
    if (ms->stamp == self.startingStamp) {
        if (auto dict = ms->any_dictionary) {
            if (self.iterator != dict->end()) {
                otio::any a = cxx_any_to_otio_any(cxxAny);
                std::swap(self.iterator->second, a);
            }
        }
    }
}

- (bool) lessThan:(CxxAnyDictionaryIterator*) rhs {
    return self.position < rhs.position;
}

- (bool) equal:(CxxAnyDictionaryIterator*) rhs {
    return self.position == rhs.position;
}

- (int) distanceTo:(CxxAnyDictionaryIterator*) rhs {
    return rhs.position - self.position;
}

@end
