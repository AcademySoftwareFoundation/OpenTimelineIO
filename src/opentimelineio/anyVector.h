// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

#include <any>
#include <assert.h>
#include <vector>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief This class provides a replacement for "std::vector<std::any>".
///
/// This class has exactly the same API as "std::vector<std::any>", except
/// that it records a "time-stamp" that lets external observers know when
/// the vector has been destroyed (which includes the case of the vector
/// being relocated in memory).
///
/// This allows us to hand out iterators that can be aware of moves
/// and take steps to safe-guard themselves from causing a crash.
class OTIO_API_TYPE AnyVector : private std::vector<std::any>
{
public:
    using vector::vector;

    /// @brief Create an empty vector.
    AnyVector()
        : _mutation_stamp{}
    {}

    /// @brief Create a copy of a vector.
    ///
    /// To be safe, avoid brace-initialization so as to not trigger
    /// list initialization behavior in older compilers:
    AnyVector(const AnyVector& other)
        : vector(other)
        , _mutation_stamp{ nullptr }
    {}

    /// @brief Destructor.
    ~AnyVector()
    {
        if (_mutation_stamp)
        {
            _mutation_stamp->any_vector = nullptr;
        }
    }

    /// @brief Copy operator.
    AnyVector& operator=(const AnyVector& other)
    {
        vector::operator=(other);
        return *this;
    }

    /// @brief Move operator.
    AnyVector& operator=(AnyVector&& other)
    {
        vector::operator=(other);
        return *this;
    }

    /// @brief Copy operator.
    AnyVector& operator=(std::initializer_list<value_type> ilist)
    {
        vector::operator=(ilist);
        return *this;
    }

    using vector::assign;
    using vector::get_allocator;

    using vector::at;
    using vector::operator[];
    using vector::back;
    using vector::data;
    using vector::front;

    using vector::begin;
    using vector::cbegin;
    using vector::cend;
    using vector::crbegin;
    using vector::crend;
    using vector::end;
    using vector::rbegin;
    using vector::rend;

    using vector::capacity;
    using vector::empty;
    using vector::max_size;
    using vector::reserve;
    using vector::shrink_to_fit;
    using vector::size;

    using vector::clear;
    using vector::emplace;
    using vector::emplace_back;
    using vector::erase;
    using vector::insert;
    using vector::pop_back;
    using vector::push_back;
    using vector::resize;
    using vector::swap;

    using vector::allocator_type;
    using vector::const_iterator;
    using vector::const_pointer;
    using vector::const_reference;
    using vector::const_reverse_iterator;
    using vector::difference_type;
    using vector::iterator;
    using vector::pointer;
    using vector::reference;
    using vector::reverse_iterator;
    using vector::size_type;
    using vector::value_type;

    /// @brief Swap vectors.
    void swap(AnyVector& other) { vector::swap(other); }

    /// @brief This struct provides a mutation time stamp.
    struct MutationStamp
    {
        /// @brief Create a new time stamp.
        MutationStamp(AnyVector* v)
            : any_vector{ v }
            , owning{ false }
        {
            assert(v != nullptr);
        }

        MutationStamp(MutationStamp const&)            = delete;
        MutationStamp& operator=(MutationStamp const&) = delete;

        /// @brief Destructor.
        ~MutationStamp()
        {
            if (any_vector)
            {
                any_vector->_mutation_stamp = nullptr;
                if (owning)
                {
                    delete any_vector;
                }
            }
        }

        AnyVector* any_vector;
        bool       owning;

    protected:
        MutationStamp()
            : any_vector{ new AnyVector }
            , owning{ true }
        {
            any_vector->_mutation_stamp = this;
        }
    };

    /// @brief Get or create a mutation time stamp.
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
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
