// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

/// @file safely_typed_any.h
///
/// This file/interface exists only so that we can package/unpackage
/// types with code compiled in one specific library to avoid the type-aliasing
/// problem that any's are subject to.
///
/// Specifically, if you put the same type T in an any from two different
/// libraries across a shared-library boundary, then the actual typeid the any
/// records depends on the library that actually packaged the any. Ditto when
/// trying to pull it out.
///
/// The solution is to have all the unpacking/packing code for the types you
/// care about be instantiated not in headers, but in source code, within one
/// common library. That's why the seemingly silly code in safely_typed_any.cpp
/// exists.

#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/color.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @name Any Create
///@{

OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(bool&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(int&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(int64_t&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(uint64_t&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(double&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(std::string&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(RationalTime&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(TimeRange&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(Color&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(TimeTransform&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(IMATH_NAMESPACE::V2d&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(IMATH_NAMESPACE::Box2d&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(AnyVector&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(AnyDictionary&&);
OPENTIMELINEIO_EXPORT std::any create_safely_typed_any(SerializableObject*);

///@}

/// @name Any Casting
///@{

OPENTIMELINEIO_EXPORT bool                   safely_cast_bool_any(std::any const& a);
OPENTIMELINEIO_EXPORT int                    safely_cast_int_any(std::any const& a);
OPENTIMELINEIO_EXPORT int64_t                safely_cast_int64_any(std::any const& a);
OPENTIMELINEIO_EXPORT uint64_t               safely_cast_uint64_any(std::any const& a);
OPENTIMELINEIO_EXPORT double                 safely_cast_double_any(std::any const& a);
OPENTIMELINEIO_EXPORT std::string            safely_cast_string_any(std::any const& a);
OPENTIMELINEIO_EXPORT RationalTime           safely_cast_rational_time_any(std::any const& a);
OPENTIMELINEIO_EXPORT TimeRange              safely_cast_time_range_any(std::any const& a);
OPENTIMELINEIO_EXPORT TimeTransform          safely_cast_time_transform_any(std::any const& a);
OPENTIMELINEIO_EXPORT Color                  safely_cast_color_any(std::any const& a);
OPENTIMELINEIO_EXPORT IMATH_NAMESPACE::V2d   safely_cast_point_any(std::any const& a);
OPENTIMELINEIO_EXPORT IMATH_NAMESPACE::Box2d safely_cast_box_any(std::any const& a);

OPENTIMELINEIO_EXPORT SerializableObject* safely_cast_retainer_any(std::any const& a);

OPENTIMELINEIO_EXPORT AnyDictionary safely_cast_any_dictionary_any(std::any const& a);
OPENTIMELINEIO_EXPORT AnyVector     safely_cast_any_vector_any(std::any const& a);

/// @bug Don't use these unless you know what you're doing...
OPENTIMELINEIO_EXPORT AnyDictionary& temp_safely_cast_any_dictionary_any(std::any const& a);
OPENTIMELINEIO_EXPORT AnyVector&     temp_safely_cast_any_vector_any(std::any const& a);

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
