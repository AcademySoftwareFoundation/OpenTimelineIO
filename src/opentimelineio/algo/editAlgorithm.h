// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace algo {

//! Enum used by 3/4 Point Edit (aka. as fill)
enum class ReferencePoint
{
    Source,
    Sequence,
    Fit
};

// Overwrite an item or items.
//
// | A | B |  ->  |A| C |B|
//   ^   ^
//   | C |
//
//          item = item to overwrite (usually a clip)
//   composition = usually a track item.
//         range = time range to overwrite.
// remove_transitions = whether to remove transitions within range.
// fill_template = item to fill in (usually a gap),
//                 when range > composition's time.
void overwrite(
    Item*            item,
    Composition*     composition,
    TimeRange const& range,
    bool             remove_transitions = true,
    Item*            fill_template      = nullptr,
    ErrorStatus*     error_status       = nullptr);

// Insert an item.
// |     A     | B |  ->  | A | C | A | B |
//       ^
//     | C |
//
//          item = item to insert (usually a clip)
//   composition = usually a track item.
//          time = time to insert at.  If < composition's start time, it will insert at 0 index.
//                                     If > composition's end_time_exclusive, it will append at end.
// remove_transitions = whether to remove transitions that intersect time.
// fill_template = item to fill in (usually a gap),
//                 when time > composition's time.
void insert(
    Item* const         item,
    Composition*        composition,
    RationalTime const& time,
    bool const          remove_transitions = true,
    Item*               fill_template      = nullptr,
    ErrorStatus*        error_status       = nullptr);

//
// Adjust a single item's start time or duration.
//
// |    A    | B | C |  ->  |  A  |FILL| B | C |
//        <--*
//            
//          item = Item to apply trim to (usually a clip)
//      delta_in = RationalTime that the item's source_range().start_time()
//                 will be adjusted by
//     delta_out = RationalTime that the item's
//                 source_range().end_time_exclusive() will be adjusted by
// fill_template = item to fill in (usually a gap),
//                 when time > composition's time.
void trim(
    Item*               item,
    RationalTime const& delta_in,
    RationalTime const& delta_out,
    Item*               fill_template = nullptr,
    ErrorStatus*        error_status  = nullptr);

// Slice an item.
//
// | A | B | -> |A|A| B |
//   ^
// composition = usually a track item.
//        time = time to slice at.
void slice(
    Composition*        composition,
    RationalTime const& time,
    bool const          remove_transitions = true,
    ErrorStatus*        error_status       = nullptr);

//
// Slip an item start_time by + or -, clamping to available_range if available.
//
// |   A   |
//  <----->
//
//          item = item to slip (usually a clip)
//         delta = +/- rational time to slip the item by.
void slip(Item* item, RationalTime const& delta);

//
// Slide an item start_time by + or -, moving the previous item's duration.
// Clamps previous item's duration to available_range if available.
//
// | A | B | C |  ->  | A     | B | C |
//     *--->
//
//          item = item to slip (usually a clip)
//         delta = +/- rational time to slide the item by.
void slide(Item* item, RationalTime const& delta);

//
// Adjust a source_range without affecting any other items.
//
// |   A   |   B   |  ->  | A |  B  |FILL|
//      <--*
//            
//      item = Item to apply ripple to (usually a clip)
//  delta_in = RationalTime that the item's source_range().start_time()
//             will be adjusted by
// delta_out = RationalTime that the item's
//             source_range().end_time_exclusive() will be adjusted by
void ripple(
    Item*               item,
    RationalTime const& delta_in,
    RationalTime const& delta_out,
    ErrorStatus*        error_status = nullptr);

//
// Adjust a source_range without affecting any other items.
//
// |   A   |   B   |  ->  | A |  B      |
//      <--*
//            
//      item = Item to apply ripple to (usually a clip)
//  delta_in = RationalTime that the item's source_range().start_time()
//             will be adjusted by
// delta_out = RationalTime that the item's
//             source_range().end_time_exclusive() will be adjusted by
void roll(
    Item*               item,
    RationalTime const& delta_in,
    RationalTime const& delta_out,
    ErrorStatus*        error_status = nullptr);

// Create a 3/4 Point Edit or Fill.
//
// | A |GAP| B |  ->  | A | C | B |
//     ^   ^
//  C--| C |--C
//
//            item = item to place onto the track (usually a clip)
//           track = track that will now own this item.
//      track_time = RationalTime
// reference_point = For 4 point editing, the reference point dictates what
//                   transform to use when running the fill.
//
void fill(
    Item*                item,
    Composition*         track,
    RationalTime const&  track_time,
    ReferencePoint const reference_point = ReferencePoint::Source,
    ErrorStatus*         error_status = nullptr);

//
// Remove item(s) at a time and fill them, optionally with a gap.
//            
// | A | C | B |  ->  | A |GAP| B |
//       ^
//       |
//
//           track = track to remove item from.
//            time = RationalTime
//            fill = whether to fill the hole with fill_template.
//   fill_template = if nullptr, use a gap to fill the hole.
//
void remove(
    RationalTime const& time,
    Composition*        composition,
    bool         const  fill = true,
    Item*               fill_template = nullptr,
    ErrorStatus*        error_status = nullptr);

}}} // namespace opentimelineio::OPENTIMELINEIO_VERSION::algo
