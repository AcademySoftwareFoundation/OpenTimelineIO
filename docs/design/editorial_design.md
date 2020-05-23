Designing an Edit API
=====================

# Design Overview
The industry is full of timeline management software but nearly all of them include a fundamental set of tools for manipulation. The most well known being:

- Overwrite
- Trim
- Cut
- Slip
- Slide
- Ripple
- Roll
- Fill (3/4 Point Edit)

OpenTimelineIO, while not seeking to become a fully realized NLE, could benefit from having a simple toolkit to help automate building/modifying timelines based on time rather than index alone.

## Structure
The underlying implementation for these edit commands will be in C++, possibly under a new library called `openedit`. This has the benefit of connecting with other languages more simply (Python, Swift, C, etc.) and, hopefully, we only need expose the functionality to the bindings.

```
OpenTimelineIO/
    `- src/
        `- opentime/
        `- opentimelineio/
        `- openedit/
            `- ...
```

The benefit for the extra library is the edit suite will inevitably grow and will begin crowding the core model, which ultimately should be able to run without it.

## Dependencies / Namespaces
The `openedit` library will have to communicate with both `opentime` and `openedit`.

This will warrant either a new namespace `namespace openedit { ... }` or using `opentimelineio` again. The latter makes some of the bellow comments less challenging but again, might pollute an otherwise clean namespace.

### ErrorStatus
This will present challenges when interfacing with the `ErrorStatus` of the different namespaces. That said, with a simple wrapper for this, we could have the instances auto convert as required.

### Retainer
Ideally, we continue to use the `Retainer<>` where possible to make sure editing is reference counted. Namespaces might make the names a bit clunky, seeing `SerializedObject::Retainer<>` all over:

```
namespace openedit { OPENEDIT_VERSION {

using namespace opentimelineio::OPENTIMELINEIO_VERSION;
auto item = SerializedObject::Retainer<Item>(...);

} }
```

So perhaps establishing some common aliases early might help?
```
using RetainedItem = SerializedObject::Retainer<Item>;
using RetainedComposition = SerializedObject::Retainer<Composition>;
...
```

# Editing Commands
Let's go through some of the most common commands and what the possibly python API might look like:

## Overwrite

![Overwrite](../../_static/edit/01_overwrite.png)
- Anything overlapping is destroyed on contact. This may split an item.

#### API
```py
"""
Args:
    item: Item that we're going to place onto the track
    track: Track that this item will belong to afterwards
    composition_time: RationalTime in our composition to put
        this item
    fill_template: Optional[Item] that will be cloned where required
        to fill in the event that this overwrite extends the end of the
        composition's limit
"""
otio.algorithms.overwrite(
    item: Item,
    track: Track,
    composition_time: RationalTime,
    fill_template: Item = None, # Default to Gap
)
```
- In the image, Clip `C` is `item` and `comp` is the track `A` and `B` are on.

----

## Insert
![Insert](../_static/edit/02_insert.png)
- Items past the in point are shifted by the new items duration.
- Item may be split if required.

#### API
```py
"""
Args:
    <same as overwrite>
"""
otio.algorithms.insert(
    item: Item,
    track: Track,
    composition_time: RationalTime,
    fill_template: Item = None, # Default to Gap
)
```

---

## Trim
![Trim](../_static/03_trim.png)
- Adjust a single item's start time or duration.
- Do not affect other clips.
- Fill now-empty time with gap or template.
- Clamps source_range to non-gap boundary (can only overwrite gaps)

#### API
```py
"""
Args:
    item: Item to apply trim to
    delta_in: RationalTime that the item's source_range().start_time()
        will be adjusted by
    delta_out: RationalTime that the item's
        source_range().end_time_exclusive() will be adjusted by
"""
otio.algorithms.trim(
    item: Item,
    delta_in: RationalTime = None,   #< Duration of change
    delta_out: RationalTime = None,  #< Duration of change
    fill_template: Item = None,      #< Default to Gap
)
```
> Not convinced on the argument names for this

---

## Slice
![Slice](../_static/04_slice.png)
- Slice an item, generating a clone of self and augment both item's source_range.

#### API
```py
"""
Args:
    item: otio.schema.Item - to cut
    at_time: otio.schema.RationalTime - time, based on the
        coordinates to slice at
    coordinates: Enumerator for the variable calculations that
        can be done to the at_time.

Example:
    Let item = A
    let at_time = 25 @ 24fps

    0                                             N
    | ------------------------------------------- |
    | [0    GAP  20][0       A      50]           |
    | ------------------------------------------- |

    if coordinates == Local:
    | ------------------------------------------- |
    | [0    GAP  20][0    A   25][26   A  50]     |
    | ------------------------------------------- |

    if coordinates == Parent:
    | ------------------------------------------- |
    | [0    GAP  20][0 A 5][6   A  50]            |
    | ------------------------------------------- |

    if coordinates == Global:
        - This only matters if the parent is a track in a compound
          stack, at which point we might be better off having the
          user just convert from one time to the other
"""
otio.algorithms.slice(
    item: Item,
    at_time: RationalTime,
    coordinates: otio.algorithms.Coordinates.(Local|Parent|Global*)
)
```
> I'm not sure if we have a coordinate enumerator already?

---


## Slip
![Slip](../_static/05_slip)
- Adjust the start_time of an item's source_range.
- Do not affect surrounding items.
- Clamp to available_range of media (if available)

#### API
```py
"""
Args:
    item: Item that we're slipping
    delta: RationalTime to adjust the range by.
"""
otio.algorithms.slip(
    item: Item,
    delta: RationalTime,
)
```
- In the example image, `C` is `item` and `delta` is the arrow's vector.

> Effectively this is already quite simple in the core API but would be nice to have here.

---


## Slide
![Slide](../_static/06_slide.png)
- Adjust start time of item and trim adjacent items to fill
- Do not change main item's duration, only adjacent
- Clamp to available range of adjacent items (if available)

#### API
```py
"""
Args:
    item: The item to push and pull around, which may in turn affect the
        items around it.
    delta: The delta that we're looking to push this item about.
"""
otio.algorithms.slide(
    item: Item,
    delta: RationalTime, # Relative like slide
)
```
- In the example image, `C` is `item` and `delta` is the arrow's vector. The edit command does the rest of the item management for us.

---

## Ripple
![Ripple](../_static/07_ripple.png)
- Adjust a source_range without adjusting any other items
- This effectively shifts all currently adjacent items to stay at the edges
- No items _before_ the item are moved/affected
- (Impl detail for otio, this is the same as adjusting the source_range of the item)

#### API
```py
"""
Args:
    item: The item to initiate the edit on
    delta_in: see trim()
    delta_out: see trim()
"""
otio.algorithms.ripple(
    item: Item,
    delta_in: RationalTime = None,   #< Duration of change
    delta_out: RationalTime = None,  #< Duration of change
)
```
- In the example image, `A` is item and `delta_out` is a negative RationalTime. The edit command shifts `B` without adjusting it's source_range.

> Again, no crazy about the argument names

---


## Roll
![Roll](../_static/09_roll.png)
- Any trim-like action results in adjacent items source_range being adjusted to fit
- No new items are ever created
- Clamped to available media (if available)

#### API
````py
"""
Args:
    item: The item to initiate the edit on
    delta_in: see trim()
    delta_out: see trim()
"""
otio.algorithms.roll(
    item: Item,
    delta_in: RationalTime = None,   #< Duration of change
    delta_out: RationalTime = None,  #< Duration of change
)
````
- In the example image, `A` is the item and `delta_out` is a negative RationalTime. The edit command augments `B` without changing it's `source_range().end_time_exclusive()`
- If `delta_in` is supplied, the item to the left of `A` would be modified (if any) - otherwise we may need to add a `Gap` / fill template.

---

## 3/4 Point Edit
![3_4 Point Edit](../_static/08_pointedit.png)
- The most complex - this "fills" a gap based on a source in/out point _or_ track in/out point
- Often used to patch in items as edit is built
- Note: This can be accomplished by a conjunction of commands above

### API
```py
"""
Args:
    item: The item to place onto the track
    track: Track that will now own this item
    replace: Item (or RT?) that we will effectively replace
    reference_point: For 4 point editing, the reference point dictates what
        transform to use when running the fill.

        Options:
            - Source   : Don't modify the source, overwrite if required
            - Sequence : Don't modify the sequence, trim item if required
            - Fit      : Apply Time Effect
"""
otio.algorithms.fill(
    item: Item,
    track: Track,
    replace: Item = None, # Alternatively, we could have a parent-coord
                          # RationalTime to find the item for us
    reference_point: otio.algorithms.ReferencePoint.Source
)
```
- This may still require some additional tinkering.


# Expanded Implementation

## Proposal
For editing commands, we should strive to do all validation and assert that everything "works" before committing anything on the timeline. A simple atomic command structure will provide that level of sophistication.

```cpp
class EditEvent {
public:
    EditEventKind kind; // e.g. Insert, Append, Remove, Modify
    Retainer<Composition> parent;
    Retainer<Item> composable;

    // ... Additional fields to execute the above as required

    bool run(ErrorStatus* error_status);
    bool revert();
};
```
An event is atomic in nature and does "one thing" to an `Item`. Each edit maneuver (e.g. `otio.algorithms.overwrite(...)`) would generate a vector of these events that can be played forward and, possibly, backward. The result of them collectively is the commands result.

```cpp
for (EditEvent &event: events) {
    event.run(error_status);
    if (*error_status) {
        for (auto it = completed_events.rbegin(); /*...*/)
            (*it).revert();
        break;
    }
    completed_events.push_back(event);
}
```

## Overall
Many of the commands mentioned have common code paths and math that is required. We can streamline many of the placement commands into a single call with different options. We can then expose that as a raw edit platform while giving users the common algorithms for ease-of-use.

