// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

/**
 * This file/interface exists only so that we can package/unpackage
 * types with code compiled in one specific library to avoid the
 * type-aliasing problem that any's are subject to.
 *
 * Specifically, if you put the same type T in an any from two
 * different libraries across a shared-library boundary, then
 * the actual typeid the any records depends on the library that
 * actually packaged the any.  Ditto when trying to pull it out.
 *
 * The solution is to have all the unpacking/packing code for the
 * types you care about be instantiated not in headers, but in source
 * code, within one common library.  That's why the seemingly
 * silly code in safely_typed_any.cpp exists.
 */

#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

any create_safely_typed_any(bool&&);
any create_safely_typed_any(int&&);
any create_safely_typed_any(int64_t&&);
any create_safely_typed_any(uint64_t&&);
any create_safely_typed_any(double&&);
any create_safely_typed_any(std::string&&);
any create_safely_typed_any(RationalTime&&);
any create_safely_typed_any(TimeRange&&);
any create_safely_typed_any(TimeTransform&&);
any create_safely_typed_any(IMATH_NAMESPACE::V2d&&);
any create_safely_typed_any(IMATH_NAMESPACE::Box2d&&);
any create_safely_typed_any(AnyVector&&);
any create_safely_typed_any(AnyDictionary&&);
any create_safely_typed_any(SerializableObject*);

bool          safely_cast_bool_any(any const& a);
int           safely_cast_int_any(any const& a);
int64_t       safely_cast_int64_any(any const& a);
uint64_t      safely_cast_uint64_any(any const& a);
double        safely_cast_double_any(any const& a);
std::string   safely_cast_string_any(any const& a);
RationalTime  safely_cast_rational_time_any(any const& a);
TimeRange     safely_cast_time_range_any(any const& a);
TimeTransform safely_cast_time_transform_any(any const& a);
IMATH_NAMESPACE::V2d    safely_cast_point_any(any const& a);
IMATH_NAMESPACE::Box2d  safely_cast_box_any(any const& a);

SerializableObject* safely_cast_retainer_any(any const& a);

AnyDictionary safely_cast_any_dictionary_any(any const& a);
AnyVector     safely_cast_any_vector_any(any const& a);

// don't use these unless you know what you're doing...
AnyDictionary& temp_safely_cast_any_dictionary_any(any const& a);
AnyVector&     temp_safely_cast_any_vector_any(any const& a);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
