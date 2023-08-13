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
    TimeRange const& time,
    ErrorStatus*     error_status = nullptr);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
