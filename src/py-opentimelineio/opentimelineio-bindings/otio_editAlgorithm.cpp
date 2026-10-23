// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>

#include "otio_errorStatusHandler.h"

#include <opentimelineio/algo/editAlgorithm.h>

using namespace OTIO_NS;
using namespace OTIO_NS::algo;

namespace py = pybind11;
using namespace pybind11::literals;

void otio_edit_algorithm_bindings(pybind11::module m)
{
    auto malgo = m.def_submodule("algo");

    py::enum_<ReferencePoint>(malgo, "ReferencePoint",
R"docstring(
The reference point used by :func:`fill` for a 3/4 point edit.
)docstring")
        .value(
            "Source",
            ReferencePoint::Source,
            "Place the item with its own duration, overwriting past the gap if "
            "it is longer.")
        .value(
            "Sequence",
            ReferencePoint::Sequence,
            "Place a copy of the item, trimmed to fit the gap.")
        .value(
            "Fit",
            ReferencePoint::Fit,
            "Place a new item with a time warp that fits it to the gap.");

    malgo.def(
        "overwrite",
        [](Item*            item,
           Composition*     composition,
           TimeRange const& range,
           bool             remove_transitions,
           Item*            fill_template) {
            overwrite(
                item,
                composition,
                range,
                remove_transitions,
                fill_template,
                ErrorStatusHandler());
        },
        "item"_a,
        "composition"_a,
        "range"_a,
        "remove_transitions"_a = true,
        "fill_template"_a      = nullptr,
        R"docstring(
Overwrite the items in a range of a composition with an item.

::

    | A | B |  ->  |A| C |B|
      ^   ^
      | C |

Items partly in the range are trimmed and items wholly in it are removed. If
the range starts after the end of the composition, the hole is filled with
``fill_template``.

:param Item item: The item to overwrite with (usually a clip).
:param Composition composition: The composition (usually a track).
:param TimeRange range: The range to overwrite.
:param bool remove_transitions: Whether to remove transitions in the range.
:param Item fill_template: The item that fills holes; a gap if None.
)docstring");

    malgo.def(
        "insert",
        [](Item*               item,
           Composition*        composition,
           RationalTime const& time,
           bool                remove_transitions,
           Item*               fill_template) {
            insert(
                item,
                composition,
                time,
                remove_transitions,
                fill_template,
                ErrorStatusHandler());
        },
        "item"_a,
        "composition"_a,
        "time"_a,
        "remove_transitions"_a = true,
        "fill_template"_a      = nullptr,
        R"docstring(
Insert an item into a composition, splitting the item at that time.

::

    |     A     | B |  ->  | A | C | A | B |
          ^
        | C |

The composition becomes longer by the item's duration. A time before the start
inserts at the start, and a time after the end appends, filling the hole with
``fill_template``.

:param Item item: The item to insert (usually a clip).
:param Composition composition: The composition (usually a track).
:param RationalTime time: The time to insert at.
:param bool remove_transitions: Whether to remove transitions at the time.
:param Item fill_template: The item that fills holes; a gap if None.
)docstring");

    malgo.def(
        "trim",
        [](Item*               item,
           RationalTime const& delta_in,
           RationalTime const& delta_out,
           Item*               fill_template) {
            trim(
                item,
                delta_in,
                delta_out,
                fill_template,
                ErrorStatusHandler());
        },
        "item"_a,
        "delta_in"_a,
        "delta_out"_a,
        "fill_template"_a = nullptr,
        R"docstring(
Adjust the start or end of an item without moving the other items.

::

    |    A    | B | C |  ->  |  A  |FILL| B | C |
           <--*

Time left empty is filled with ``fill_template``, or added to a neighboring
gap.

:param Item item: The item to trim (usually a clip).
:param RationalTime delta_in: The amount to adjust the start by.
:param RationalTime delta_out: The amount to adjust the end by.
:param Item fill_template: The item that fills holes; a gap if None.
)docstring");

    malgo.def(
        "slice",
        [](Composition*        composition,
           RationalTime const& time,
           bool                remove_transitions) {
            slice(composition, time, remove_transitions, ErrorStatusHandler());
        },
        "composition"_a,
        "time"_a,
        "remove_transitions"_a = true,
        R"docstring(
Split the item at a time into two items.

::

    | A | B |  ->  |A|A| B |
      ^

:param Composition composition: The composition (usually a track).
:param RationalTime time: The time to split at.
:param bool remove_transitions: Whether to remove transitions at the time.
)docstring");

    malgo.def(
        "slip",
        [](Item* item, RationalTime const& delta) { slip(item, delta); },
        "item"_a,
        "delta"_a,
        R"docstring(
Move an item's source range without changing its duration or the other items.

::

    |   A   |
     <----->

The source range is clamped to the media's available range, if there is one.

:param Item item: The item to slip (usually a clip).
:param RationalTime delta: The amount to move the source range by.
)docstring");

    malgo.def(
        "slide",
        [](Item* item, RationalTime const& delta) { slide(item, delta); },
        "item"_a,
        "delta"_a,
        R"docstring(
Move an item by changing the duration of the item before it.

::

    | A | B | C |  ->  | A     | B | C |
        *--->

The previous item is clamped to its media's available range, if there is one.
The first item in a composition is not changed.

:param Item item: The item to slide (usually a clip).
:param RationalTime delta: The amount to move the item by.
)docstring");

    malgo.def(
        "ripple",
        [](Item*               item,
           RationalTime const& delta_in,
           RationalTime const& delta_out) {
            ripple(item, delta_in, delta_out, ErrorStatusHandler());
        },
        "item"_a,
        "delta_in"_a,
        "delta_out"_a,
        R"docstring(
Adjust the start or end of an item without changing the other items, so
the items after it move.

::

    |   A   |   B   |  ->  | A |   B   |
         <--*

:param Item item: The item to ripple (usually a clip).
:param RationalTime delta_in: The amount to adjust the start by.
:param RationalTime delta_out: The amount to adjust the end by.
)docstring");

    malgo.def(
        "roll",
        [](Item*               item,
           RationalTime const& delta_in,
           RationalTime const& delta_out) {
            roll(item, delta_in, delta_out, ErrorStatusHandler());
        },
        "item"_a,
        "delta_in"_a,
        "delta_out"_a,
        R"docstring(
Adjust the start or end of an item, adjusting the neighboring items to fit.

::

    |   A   |   B   |  ->  | A |  B      |
         <--*

No items are added, and the items before and after keep their positions.
Adjustments are clamped to the media's available range, if there is one.

:param Item item: The item to roll (usually a clip).
:param RationalTime delta_in: The amount to adjust the start by.
:param RationalTime delta_out: The amount to adjust the end by.
)docstring");

    malgo.def(
        "fill",
        [](Item*               item,
           Composition*        track,
           RationalTime const& track_time,
           ReferencePoint      reference_point) {
            fill(
                item,
                track,
                track_time,
                reference_point,
                ErrorStatusHandler());
        },
        "item"_a,
        "track"_a,
        "track_time"_a,
        "reference_point"_a = ReferencePoint::Source,
        R"docstring(
Place an item into the gap at a time (a 3/4 point edit).

::

    | A |GAP| B |  ->  | A | C | B |
        ^   ^
     C--| C |--C

:param Item item: The item to place (usually a clip).
:param Composition track: The track to place the item in.
:param RationalTime track_time: A time in the gap.
:param ReferencePoint reference_point: How to fit the item to the gap.
)docstring");

    malgo.def(
        "remove",
        [](Composition*        composition,
           RationalTime const& time,
           bool                fill,
           Item*               fill_template) {
            remove(
                composition,
                time,
                fill,
                fill_template,
                ErrorStatusHandler());
        },
        "composition"_a,
        "time"_a,
        "fill"_a          = true,
        "fill_template"_a = nullptr,
        R"docstring(
Remove the item at a time.

::

    | A | C | B |  ->  | A |GAP| B |
          ^

:param Composition composition: The composition (usually a track).
:param RationalTime time: The time of the item to remove.
:param bool fill: Whether to fill the hole; if False the items after move up.
:param Item fill_template: The item that fills the hole; a gap if None.
)docstring");
}
