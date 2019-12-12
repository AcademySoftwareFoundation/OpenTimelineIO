//
//  CxxVectorProperty.h
//  otio-swift
//
//  Created by David Baraff on 3/1/19.
//
#import <Foundation/Foundation.h>
#import "CxxRetainer.h"

#if defined(__cplusplus)
#import <opentimelineio/serializableObject.h>
namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

class CxxSOVectorBase {
public:
    CxxSOVectorBase();
    CxxSOVectorBase& operator=(CxxSOVectorBase const&) = delete;
    CxxSOVectorBase(CxxSOVectorBase const&) = delete;
    virtual ~CxxSOVectorBase();
    
    virtual otio::SerializableObject* _Nullable fetch(int index) = 0;
    virtual int size() = 0;
    virtual void clear() = 0;
    
    virtual void store(int index, otio::SerializableObject* _Nonnull) = 0;
    virtual void moveIndex(int fromIndex, int toIndex) = 0;
    virtual void removeAtEnd() = 0;
    virtual void append(otio::SerializableObject* _Nonnull) = 0;
    virtual void shrinkOrGrow(int n, bool grow) = 0;
    virtual void setContents(CxxSOVectorBase* _Nonnull src, bool destroyingSrc) = 0;
};

template <typename T>
class CxxSOVector : public CxxSOVectorBase {
public:
    CxxSOVector()
    : _v{* new std::vector<otio::SerializableObject::Retainer<T>>}, _owner{true}
    {
    }
    
    CxxSOVector(std::vector<otio::SerializableObject::Retainer<T>>& v)
    : _v{v}, _owner{false} {
    }

    virtual otio::SerializableObject* _Nullable fetch(int index) {
        return index < _v.size() ? _v[index] : nullptr;
    }
    
    virtual int size() {
        return int(_v.size());
    }
    
    virtual ~CxxSOVector() {
        if (_owner) {
            delete &_v;
        }
    }
    
    virtual void clear() {
        _v.clear();
    }

    virtual void store(int index, otio::SerializableObject* _Nonnull so) {
        if (index >= 0 && index < _v.size()) {
            _v[index] = std::move(otio::SerializableObject::Retainer<T>((T*)so));
        }
        else {
            _v.emplace_back(otio::SerializableObject::Retainer<T>((T*)so));
        }
    }
    
    virtual void moveIndex(int fromIndex, int toIndex) {
        std::swap(_v[fromIndex], _v[toIndex]);
    }
    
    virtual void append(otio::SerializableObject* _Nonnull so) {
        _v.emplace_back(otio::SerializableObject::Retainer<T>((T*)so));
    }
    
    virtual void removeAtEnd() {
        _v.pop_back();
    }
    
    virtual void shrinkOrGrow(int n, bool grow) {
        if (grow) {
            for (int i = 0; i < n; i++) {
                _v.push_back(otio::SerializableObject::Retainer<T>());
            }
        }
        else {
            if (n >= _v.size()) {
                _v.clear();
                return;
            }
            
            for (int i = 0; i < n; i++) {
                _v.pop_back();
            }
        }
    }
    
    virtual void setContents(CxxSOVectorBase* _Nonnull src, bool destroyingSrc) {
        CxxSOVector* typedSrc = (CxxSOVector*) src;
        if (destroyingSrc) {
            std::swap(_v, typedSrc->_v);
        }
        else {
            _v = typedSrc->_v;
        }
    }

private:
    std::vector<otio::SerializableObject::Retainer<T>>& _v;
    bool _owner;
};

#endif

NS_ASSUME_NONNULL_BEGIN

@interface CxxVectorProperty : NSObject
- (instancetype) init;
- (int) count;
- (void* _Nullable) cxxSerializableObjectAtIndex:(int) index;
- (void) clear;

- (void) store:(int) index
         value:(void*) cxxSerializableObject;
- (void) moveIndex:(int) fromIndex
           toIndex:(int) toIndex;
- (void) addAtEnd:(void*) cxxSerializableObject;
- (void) shrinkOrGrow:(int) n
                 grow:(bool) grow;
- (void) copyContents:(CxxVectorProperty*) src;
- (void) moveContents:(CxxVectorProperty*) src;

@property(weak) CxxRetainer* cxxRetainer;
@end

#if defined(__cplusplus)
@interface CxxVectorProperty ()
@property CxxSOVectorBase* _Nullable  cxxVectorBase;
@end
#endif

NS_ASSUME_NONNULL_END
