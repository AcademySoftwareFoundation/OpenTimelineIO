// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

// Slice an item.
//
// | A | B | -> |A|A| B |
//   ^
void edit_slice(
    Composition*        composition,
    RationalTime const& time,
    ErrorStatus*        error_status = nullptr);

// Overwrite an item or items.
//
// | A | B | -> |A| C |B|
//   ^   ^
//   | C |
void edit_overwrite(
    Item*            item,
    Composition*     composition,
    TimeRange const& range,
    ErrorStatus*     error_status = nullptr);

// Insert an item.
// |     A     | B | -> | A | C | A | B |
//       ^   
//     | C |
void edit_insert(
    Item*            item,
    Composition*     composition,
    RationalTime const& time,
    ErrorStatus*     error_status = nullptr);
        
void edit_cut(
    ErrorStatus*     error_status = nullptr);
        
void edit_slip(
    ErrorStatus*     error_status = nullptr);
        
void edit_slide(
    ErrorStatus*     error_status = nullptr);
        
void edit_ripple(
    ErrorStatus*     error_status = nullptr);
        
void edit_roll(
    ErrorStatus*     error_status = nullptr);
        
void edit_fill(
    ErrorStatus*     error_status = nullptr);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
