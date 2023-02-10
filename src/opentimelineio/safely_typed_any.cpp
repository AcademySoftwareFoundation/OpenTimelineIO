// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/safely_typed_any.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

std::any
create_safely_typed_any(bool&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(int&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(int64_t&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(uint64_t&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(double&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(std::string&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(RationalTime&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(TimeRange&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(TimeTransform&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(Imath::V2d&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(Imath::Box2d&& value)
{
    return std::any(value);
}

std::any
create_safely_typed_any(AnyVector&& value)
{
    return std::any(std::move(value));
}

std::any
create_safely_typed_any(AnyDictionary&& value)
{
    return std::any(std::move(value));
}

std::any
create_safely_typed_any(SerializableObject* value)
{
    return std::any(SerializableObject::Retainer<>(value));
}

bool
safely_cast_bool_any(std::any const& a)
{
    return std::any_cast<bool>(a);
}

int
safely_cast_int_any(std::any const& a)
{
    return std::any_cast<int>(a);
}

int64_t
safely_cast_int64_any(std::any const& a)
{
    return std::any_cast<int64_t>(a);
}

uint64_t
safely_cast_uint64_any(std::any const& a)
{
    return std::any_cast<uint64_t>(a);
}

double
safely_cast_double_any(std::any const& a)
{
    return std::any_cast<double>(a);
}

std::string
safely_cast_string_any(std::any const& a)
{
    return std::any_cast<std::string>(a);
}

RationalTime
safely_cast_rational_time_any(std::any const& a)
{
    return std::any_cast<RationalTime>(a);
}

TimeRange
safely_cast_time_range_any(std::any const& a)
{
    return std::any_cast<TimeRange>(a);
}

TimeTransform
safely_cast_time_transform_any(std::any const& a)
{
    return std::any_cast<TimeTransform>(a);
}

Imath::V2d
safely_cast_point_any(std::any const& a)
{
    return std::any_cast<Imath::V2d>(a);
}

Imath::Box2d
safely_cast_box_any(std::any const& a)
{
    return std::any_cast<Imath::Box2d>(a);
}

AnyDictionary
safely_cast_any_dictionary_any(std::any const& a)
{
    return std::any_cast<AnyDictionary>(a);
}

AnyVector
safely_cast_any_vector_any(std::any const& a)
{
    return std::any_cast<AnyVector>(a);
}

SerializableObject*
safely_cast_retainer_any(std::any const& a)
{
    return std::any_cast<SerializableObject::Retainer<> const&>(a);
}

AnyVector&
temp_safely_cast_any_vector_any(std::any const& a)
{
    return const_cast<AnyVector&>(std::any_cast<AnyVector const&>(a));
}

AnyDictionary&
temp_safely_cast_any_dictionary_any(std::any const& a)
{
    return const_cast<AnyDictionary&>(std::any_cast<AnyDictionary const&>(a));
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
