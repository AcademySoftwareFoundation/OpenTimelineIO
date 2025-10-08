// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

#include <any>
#include <assert.h>
#include <map>
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief This class provides a replacement for "std::map<std::string, std::any>".
///
/// This class has exactly the same API as "std::map<std::string, std::any>",
/// except that it records a "time-stamp" that bumps monotonically every time an
/// operation that would invalidate iterators is performed (this happens for
/// operator =, clear, erase, insert, and swap). The stamp also lets external
/// observers know when the map has been destroyed (which includes the case of
/// the map being relocated in memory).
///
/// This allows us to hand out iterators that can be aware of mutation and moves
/// and take steps to safe-guard themselves from causing a crash.  (Yes, I'm
/// talking to you, Python...)
class OTIO_API AnyDictionary : private std::map<std::string, std::any>
{
public:
    using map::map;

    /// @brief Create an empty dictionary.
    OTIO_API AnyDictionary()
        : map{}
        , _mutation_stamp{}
    {}

    /// @brief Create a copy of a dictionary.
    ///
    /// To be safe, avoid brace-initialization so as to not trigger
    /// list initialization behavior in older compilers:
    OTIO_API AnyDictionary(const AnyDictionary& other)
        : map(other)
        , _mutation_stamp{}
    {}

    /// @brief Destructor.
    OTIO_API ~AnyDictionary()
    {
        if (_mutation_stamp)
        {
            _mutation_stamp->stamp          = -1;
            _mutation_stamp->any_dictionary = nullptr;
        }
    }

    /// @brief Copy operator.
    OTIO_API AnyDictionary& operator=(const AnyDictionary& other)
    {
        mutate();
        map::operator=(other);
        return *this;
    }

    /// @brief Move operator.
    OTIO_API AnyDictionary& operator=(AnyDictionary&& other)
    {
        mutate();
        other.mutate();
        map::operator=(other);
        return *this;
    }

    /// @brief Copy operator.
    OTIO_API AnyDictionary& operator=(std::initializer_list<value_type> ilist)
    {
        mutate();
        map::operator=(ilist);
        return *this;
    }

    using map::get_allocator;

    using map::at;
    using map::operator[];

    using map::begin;
    using map::cbegin;
    using map::cend;
    using map::crbegin;
    using map::crend;
    using map::end;
    using map::rbegin;
    using map::rend;

    /// @brief Clear the dictionary.
    OTIO_API void clear() noexcept
    {
        mutate();
        map::clear();
    }
    using map::emplace;
    using map::emplace_hint;
    using map::insert;

    /// @brief Erase an item.
    OTIO_API iterator erase(const_iterator pos)
    {
        mutate();
        return map::erase(pos);
    }

    /// @brief Erase a range of items.
    OTIO_API iterator erase(const_iterator first, const_iterator last)
    {
        mutate();
        return map::erase(first, last);
    }

    /// @brief Erase an item with the given key.
    OTIO_API size_type erase(const key_type& key)
    {
        mutate();
        return map::erase(key);
    }

    /// @brief Swap dictionaries.
    OTIO_API void swap(AnyDictionary& other)
    {
        mutate();
        other.mutate();
        map::swap(other);
    }

    /// @brief Return whether the given key has been set.
    ///
    /// If key is in this, and the type of key matches the type of result, then
    /// set result to the value of std::any_cast<type>(this[key]) and return true,
    /// otherwise return false.
    template <typename containedType>
    bool get_if_set(const std::string& key, containedType* result) const
    {
        if (result == nullptr)
        {
            return false;
        }

        const auto it = this->find(key);

        if ((it != this->end())
            && (it->second.type().hash_code()
                == typeid(containedType).hash_code()))
        {
            *result = std::any_cast<containedType>(it->second);
            return true;
        }
        else
        {
            return false;
        }
    }

    /// @brief Return whether the dictionary contains the given key.
    inline bool has_key(const std::string& key) const
    {
        return (this->find(key) != this->end());
    }

    /// @brief Set the default for the given key.
    ///
    /// If key is in this, place the value in result and return true, otherwise
    /// store the value in result at key and return false.
    template <typename containedType>
    bool set_default(const std::string& key, containedType* result)
    {
        if (result == nullptr)
        {
            return false;
        }

        const auto d_it = this->find(key);

        if ((d_it != this->end())
            && (d_it->second.type().hash_code()
                == typeid(containedType).hash_code()))
        {
            *result = std::any_cast<containedType>(d_it->second);
            return true;
        }
        else
        {
            this->insert({ key, *result });
            return false;
        }
    }

    using map::empty;
    using map::max_size;
    using map::size;

    using map::count;
    using map::equal_range;
    using map::find;
    using map::lower_bound;
    using map::upper_bound;

    using map::key_comp;
    using map::value_comp;

    using map::allocator_type;
    using map::const_iterator;
    using map::const_pointer;
    using map::const_reference;
    using map::const_reverse_iterator;
    using map::difference_type;
    using map::iterator;
    using map::key_compare;
    using map::key_type;
    using map::mapped_type;
    using map::pointer;
    using map::reference;
    using map::reverse_iterator;
    using map::size_type;
    using map::value_type;

    /// @brief This struct provides a mutation time stamp.
    struct MutationStamp
    {
        /// @brief Create a new time stamp.
        constexpr MutationStamp(AnyDictionary* d) noexcept
            : stamp{ 1 }
            , any_dictionary{ d }
            , owning{ false }
        {
            assert(d);
        }

        MutationStamp(MutationStamp const&)            = delete;
        MutationStamp& operator=(MutationStamp const&) = delete;

        /// @brief Destructor.
        ~MutationStamp()
        {
            if (any_dictionary)
            {
                any_dictionary->_mutation_stamp = nullptr;
                if (owning)
                {
                    delete any_dictionary;
                }
            }
        }

        int64_t        stamp;
        AnyDictionary* any_dictionary;
        bool           owning;

    protected:
        MutationStamp()
            : stamp{ 1 }
            , any_dictionary{ new AnyDictionary }
            , owning{ true }
        {
            any_dictionary->_mutation_stamp = this;
        }
    };

    /// @brief Get or crate a mutation time stamp.
    MutationStamp* get_or_create_mutation_stamp()
    {
        if (!_mutation_stamp)
        {
            _mutation_stamp = new MutationStamp(this);
        }
        return _mutation_stamp;
    }

    friend struct MutationStamp;

private:
    MutationStamp* _mutation_stamp = nullptr;

    void mutate() noexcept
    {
        if (_mutation_stamp)
        {
            _mutation_stamp->stamp++;
        }
    }
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
