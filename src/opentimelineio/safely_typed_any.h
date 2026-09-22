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

#include "opentimelineio/export.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/color.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @name Any Create
///@{

OTIO_API std::any create_safely_typed_any(bool&&);
OTIO_API std::any create_safely_typed_any(int&&);
OTIO_API std::any create_safely_typed_any(int64_t&&);
OTIO_API std::any create_safely_typed_any(uint64_t&&);
OTIO_API std::any create_safely_typed_any(double&&);
OTIO_API std::any create_safely_typed_any(std::string&&);
OTIO_API std::any create_safely_typed_any(RationalTime&&);
OTIO_API std::any create_safely_typed_any(TimeRange&&);
OTIO_API std::any create_safely_typed_any(Color&&);
OTIO_API std::any create_safely_typed_any(TimeTransform&&);
OTIO_API std::any create_safely_typed_any(IMATH_NAMESPACE::V2d&&);
OTIO_API std::any create_safely_typed_any(IMATH_NAMESPACE::Box2d&&);
OTIO_API std::any create_safely_typed_any(AnyVector&&);
OTIO_API std::any create_safely_typed_any(AnyDictionary&&);
OTIO_API std::any create_safely_typed_any(SerializableObject*);

///@}

/// @name Any Casting
///@{

OTIO_API bool                   safely_cast_bool_any(std::any const& a);
OTIO_API int                    safely_cast_int_any(std::any const& a);
OTIO_API int64_t                safely_cast_int64_any(std::any const& a);
OTIO_API uint64_t               safely_cast_uint64_any(std::any const& a);
OTIO_API double                 safely_cast_double_any(std::any const& a);
OTIO_API std::string            safely_cast_string_any(std::any const& a);
OTIO_API RationalTime           safely_cast_rational_time_any(std::any const& a);
OTIO_API TimeRange              safely_cast_time_range_any(std::any const& a);
OTIO_API TimeTransform          safely_cast_time_transform_any(std::any const& a);
OTIO_API Color                  safely_cast_color_any(std::any const& a);
OTIO_API IMATH_NAMESPACE::V2d   safely_cast_point_any(std::any const& a);
OTIO_API IMATH_NAMESPACE::Box2d safely_cast_box_any(std::any const& a);

OTIO_API SerializableObject* safely_cast_retainer_any(std::any const& a);

OTIO_API AnyDictionary safely_cast_any_dictionary_any(std::any const& a);
AnyVector     safely_cast_any_vector_any(std::any const& a);

/// @bug Don't use these unless you know what you're doing...
OTIO_API AnyDictionary& temp_safely_cast_any_dictionary_any(std::any const& a);
OTIO_API AnyVector&     temp_safely_cast_any_vector_any(std::any const& a);

///@}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
