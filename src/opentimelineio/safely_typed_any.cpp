// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/safely_typed_any.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

any
create_safely_typed_any(bool&& value)
{
    return any(value);
}

any
create_safely_typed_any(int&& value)
{
    return any(value);
}

any
create_safely_typed_any(int64_t&& value)
{
    return any(value);
}

any
create_safely_typed_any(uint64_t&& value)
{
    return any(value);
}

any
create_safely_typed_any(double&& value)
{
    return any(value);
}

any
create_safely_typed_any(std::string&& value)
{
    return any(value);
}

any
create_safely_typed_any(RationalTime&& value)
{
    return any(value);
}

any
create_safely_typed_any(TimeRange&& value)
{
    return any(value);
}

any
create_safely_typed_any(TimeTransform&& value)
{
    return any(value);
}

any
create_safely_typed_any(IMATH_NAMESPACE::V2d&& value)
{
    return any(value);
}

any
create_safely_typed_any(IMATH_NAMESPACE::Box2d&& value)
{
    return any(value);
}

any
create_safely_typed_any(AnyVector&& value)
{
    return any(std::move(value));
}

any
create_safely_typed_any(AnyDictionary&& value)
{
    return any(std::move(value));
}

any
create_safely_typed_any(SerializableObject* value)
{
    return any(SerializableObject::Retainer<>(value));
}

bool
safely_cast_bool_any(any const& a)
{
    return any_cast<bool>(a);
}

int
safely_cast_int_any(any const& a)
{
    return any_cast<int>(a);
}

int64_t
safely_cast_int64_any(any const& a)
{
    return any_cast<int64_t>(a);
}

uint64_t
safely_cast_uint64_any(any const& a)
{
    return any_cast<uint64_t>(a);
}

double
safely_cast_double_any(any const& a)
{
    return any_cast<double>(a);
}

std::string
safely_cast_string_any(any const& a)
{
    return any_cast<std::string>(a);
}

RationalTime
safely_cast_rational_time_any(any const& a)
{
    return any_cast<RationalTime>(a);
}

TimeRange
safely_cast_time_range_any(any const& a)
{
    return any_cast<TimeRange>(a);
}

TimeTransform
safely_cast_time_transform_any(any const& a)
{
    return any_cast<TimeTransform>(a);
}

IMATH_NAMESPACE::V2d
safely_cast_point_any(any const& a)
{
    return any_cast<IMATH_NAMESPACE::V2d>(a);
}

IMATH_NAMESPACE::Box2d
safely_cast_box_any(any const& a)
{
    return any_cast<IMATH_NAMESPACE::Box2d>(a);
}

AnyDictionary
safely_cast_any_dictionary_any(any const& a)
{
    return any_cast<AnyDictionary>(a);
}

AnyVector
safely_cast_any_vector_any(any const& a)
{
    return any_cast<AnyVector>(a);
}

SerializableObject*
safely_cast_retainer_any(any const& a)
{
    return any_cast<SerializableObject::Retainer<> const&>(a);
}

AnyVector&
temp_safely_cast_any_vector_any(any const& a)
{
    return const_cast<AnyVector&>(any_cast<AnyVector const&>(a));
}

AnyDictionary&
temp_safely_cast_any_dictionary_any(any const& a)
{
    return const_cast<AnyDictionary&>(any_cast<AnyDictionary const&>(a));
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
