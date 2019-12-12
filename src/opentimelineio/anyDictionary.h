#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/any.h"

#include <assert.h>
#include <map>
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
/*
 * An AnyDictionary has exactly the same API as
 *    std::map<std::string, any>
 *
 * except that it records a "time-stamp" that bumps monotonically every time an
 * operation that would invalidate iterators is performed.
 * (This happens for operator=, clear, erase, insert, swap).  The stamp also
 * lets external observers know when the map has been destroyed (which includes
 * the case of the map being relocated in memory).
 *
 * This allows us to hand out iterators that can be aware of mutation and moves
 * and take steps to safe-guard themselves from causing a crash.  (Yes,
 * I'm talking to you, Python...)
 */
class AnyDictionary : private std::map<std::string, any> {
public:
    using map::map;

    AnyDictionary() : map {}, _mutation_stamp {} {}
    
    // to be safe, avoid brace-initialization so as to not trigger
    // list initialization behavior in older compilers:
    AnyDictionary(const AnyDictionary& other) : map (other), _mutation_stamp {} {}
    
    ~AnyDictionary() {
        if (_mutation_stamp) {
            _mutation_stamp->stamp = -1;
            _mutation_stamp->any_dictionary = nullptr;
        }
    }
    
    AnyDictionary& operator=(const AnyDictionary& other) {
        mutate();
        map::operator= (other);
        return *this;
    }

    AnyDictionary& operator=(AnyDictionary&& other) {
        mutate();
        other.mutate();
        map::operator= (other);
        return *this;
    }

    AnyDictionary& operator=(std::initializer_list<value_type> ilist) {
        mutate();
        map::operator= (ilist);
        return *this;
    }

    using map::get_allocator;

    using map::at;
    using map::operator[];

    using map::begin;
    using map::cbegin;
    using map::end;
    using map::cend;
    using map::rbegin;
    using map::crbegin;
    using map::rend;
    using map::crend;

    void clear() noexcept {
        mutate();
        map::clear();
    }
    using map::insert;
    using map::emplace;
    using map::emplace_hint;

    iterator erase(const_iterator pos) {
        mutate();
        return map::erase(pos);
    }
        
    iterator erase(const_iterator first, const_iterator last) {
        mutate();
        return map::erase(first, last);
    }
    
    size_type erase(const key_type& key) {
        mutate();
        return map::erase(key);
    }

    void swap(AnyDictionary& other) {
        mutate();
        other.mutate();
        map::swap(other);
    }
    
    using map::empty;
    using map::size;
    using map::max_size;

    using map::count;
    using map::find;
    using map::equal_range;
    using map::lower_bound;
    using map::upper_bound;

    using map::key_comp;
    using map::value_comp;

    using map::key_type;
    using map::mapped_type;
    using map::value_type;
    using map::size_type;
    using map::difference_type;
    using map::key_compare;
    using map::allocator_type;
    using map::reference;
    using map::const_reference;
    using map::pointer;
    using map::const_pointer;
    using map::iterator;
    using map::const_iterator;
    using map::reverse_iterator;
    using map::const_reverse_iterator;
    
    struct MutationStamp {
        MutationStamp(AnyDictionary* d)
        : stamp {1}, any_dictionary {d}, owning {false} {
            assert(d);
        }
            
        MutationStamp(MutationStamp const&) = delete;
        MutationStamp& operator=(MutationStamp const&) = delete;

        ~MutationStamp() {
            if (any_dictionary) {
                any_dictionary->_mutation_stamp = nullptr;
                if (owning) {
                    delete any_dictionary;
                }
            }
        }

        int64_t stamp;
        AnyDictionary* any_dictionary;
        bool owning;

    protected:
        MutationStamp() : stamp {1}, any_dictionary {new AnyDictionary}, owning {true} {
            any_dictionary->_mutation_stamp = this;
        }
    };
    
    MutationStamp* get_or_create_mutation_stamp() {
        if (!_mutation_stamp) {
            _mutation_stamp = new MutationStamp(this);
        }
        return _mutation_stamp;
    }
    
    friend struct MutationStamp;
    
private:
    MutationStamp* _mutation_stamp = nullptr;
    
    void mutate() {
        if (_mutation_stamp) {
            _mutation_stamp->stamp++;
        }
    }
};

} }

