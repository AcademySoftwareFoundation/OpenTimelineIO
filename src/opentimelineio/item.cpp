// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/item.h"
#include "opentimelineio/composition.h"
#include "opentimelineio/effect.h"
#include "opentimelineio/marker.h"

#include <assert.h>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

Item::Item(
    std::string const&              name,
    std::optional<TimeRange> const& source_range,
    AnyDictionary const&            metadata,
    std::vector<Effect*> const&     effects,
    std::vector<Marker*> const&     markers,
    bool                            enabled,
    std::optional<Color> const&     color)
    : Parent(name, metadata)
    , _source_range(source_range)
    , _effects(effects.begin(), effects.end())
    , _markers(markers.begin(), markers.end())
    , _color(color)
    , _enabled(enabled)
{}

Item::~Item()
{}

bool
Item::visible() const
{
    return _enabled;
}

bool
Item::overlapping() const
{
    return false;
}

RationalTime
Item::duration(ErrorStatus* error_status) const
{
    return trimmed_range(error_status).duration();
}

TimeRange
Item::available_range(ErrorStatus* error_status) const
{
    if (error_status)
    {
        *error_status = ErrorStatus::NOT_IMPLEMENTED;
    }
    return TimeRange();
}

TimeRange
Item::visible_range(ErrorStatus* error_status) const
{
    TimeRange result = trimmed_range(error_status);
    if (parent() && !is_error(error_status))
    {
        auto head_tail = parent()->handles_of_child(this, error_status);
        if (is_error(error_status))
        {
            return result;
        }
        if (head_tail.first)
        {
            result = TimeRange(
                result.start_time() - *head_tail.first,
                result.duration() + *head_tail.first);
        }
        if (head_tail.second)
        {
            result = TimeRange(
                result.start_time(),
                result.duration() + *head_tail.second);
        }
    }
    return result;
}

std::optional<TimeRange>
Item::trimmed_range_in_parent(ErrorStatus* error_status) const
{
    if (!parent() && error_status)
    {
        *error_status                = ErrorStatus::NOT_A_CHILD;
        error_status->object_details = this;
    }

    return parent()->trimmed_range_of_child(this, error_status);
}

TimeRange
Item::range_in_parent(ErrorStatus* error_status) const
{
    if (!parent() && error_status)
    {
        *error_status                = ErrorStatus::NOT_A_CHILD;
        error_status->object_details = this;
    }

    return parent()->range_of_child(this, error_status);
}

RationalTime
Item::transformed_time(
    RationalTime time,
    Item const*  to_item,
    ErrorStatus* error_status) const
{
    if (!to_item)
    {
        return time;
    }

    auto root   = _highest_ancestor();
    auto item   = this;
    auto result = time;

    while (item != root && item != to_item)
    {
        auto parent = item->parent();
        result -= item->trimmed_range(error_status).start_time();
        if (is_error(error_status))
        {
            return result;
        }

        result += parent->range_of_child(item, error_status).start_time();
        item = parent;
    }

    auto ancestor = item;
    item          = to_item;
    while (item != root && item != ancestor)
    {
        auto parent = item->parent();
        result += item->trimmed_range(error_status).start_time();
        if (is_error(error_status))
        {
            return result;
        }

        result -= parent->range_of_child(item, error_status).start_time();
        if (is_error(error_status))
        {
            return result;
        }

        item = parent;
    }

    assert(item == ancestor);
    return result;
}

TimeRange
Item::transformed_time_range(
    TimeRange    time_range,
    Item const*  to_item,
    ErrorStatus* error_status) const
{
    return TimeRange(
        transformed_time(time_range.start_time(), to_item, error_status),
        time_range.duration());
}

bool
Item::read_from(Reader& reader)
{
    return reader.read_if_present("source_range", &_source_range)
           && reader.read_if_present("effects", &_effects)
           && reader.read_if_present("markers", &_markers)
           && reader.read_if_present("enabled", &_enabled)
           && reader.read_if_present("color", &_color)
           && Parent::read_from(reader);
}

void
Item::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("source_range", _source_range);
    writer.write("effects", _effects);
    writer.write("markers", _markers);
    writer.write("enabled", _enabled);
    writer.write("color", _color);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
