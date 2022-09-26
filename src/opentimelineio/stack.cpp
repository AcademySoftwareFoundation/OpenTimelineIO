// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/stack.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/vectorIndexing.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Stack::Stack(
    std::string const&          name,
    optional<TimeRange> const&  source_range,
    AnyDictionary const&        metadata,
    std::vector<Effect*> const& effects,
    std::vector<Marker*> const& markers)
    : Parent(name, source_range, metadata, effects, markers)
{}

Stack::~Stack()
{}

std::string
Stack::composition_kind() const
{
    static std::string kind = "Stack";
    return kind;
}

bool
Stack::read_from(Reader& reader)
{
    return Parent::read_from(reader);
}

void
Stack::write_to(Writer& writer) const
{
    Parent::write_to(writer);
}

TimeRange
Stack::range_of_child_at_index(int index, ErrorStatus* error_status) const
{
    index = adjusted_vector_index(index, children());
    if (index < 0 || index >= int(children().size()))
    {
        if (error_status)
        {
            *error_status = ErrorStatus::ILLEGAL_INDEX;
        }
        return TimeRange();
    }

    Composable* child    = children()[index];
    auto        duration = child->duration(error_status);
    if (is_error(error_status))
    {
        return TimeRange();
    }

    return TimeRange(RationalTime(0, duration.rate()), duration);
}

std::map<Composable*, TimeRange>
Stack::range_of_all_children(ErrorStatus* error_status) const
{
    std::map<Composable*, TimeRange> result;
    auto                             kids = children();

    for (size_t i = 0; i < kids.size(); i++)
    {
        result[kids[i]] = range_of_child_at_index(int(i), error_status);
        if (is_error(error_status))
        {
            break;
        }
    }

    return result;
}

TimeRange
Stack::trimmed_range_of_child_at_index(int index, ErrorStatus* error_status)
    const
{
    auto range = range_of_child_at_index(index, error_status);
    if (is_error(error_status) || !source_range())
    {
        return range;
    }

    const TimeRange sr = *source_range();
    return TimeRange(
        sr.start_time(),
        std::min(range.duration(), sr.duration()));
}

TimeRange
Stack::available_range(ErrorStatus* error_status) const
{
    if (children().empty())
    {
        return TimeRange();
    }

    auto duration = children()[0].value->duration(error_status);
    for (size_t i = 1; i < children().size() && !is_error(error_status); i++)
    {
        duration =
            std::max(duration, children()[i].value->duration(error_status));
    }

    return TimeRange(RationalTime(0, duration.rate()), duration);
}

std::vector<SerializableObject::Retainer<Clip>>
Stack::clip_if(
    ErrorStatus*               error_status,
    optional<TimeRange> const& search_range,
    bool                       shallow_search) const
{
    return children_if<Clip>(error_status, search_range, shallow_search);
}

optional<Imath::Box2d>
Stack::available_image_bounds(ErrorStatus* error_status) const
{
    optional<Imath::Box2d> box;
    bool                   found_first_child = false;
    for (auto clip: children_if<Clip>(error_status))
    {
        optional<Imath::Box2d> child_box;
        if (auto clip_box = clip->available_image_bounds(error_status))
        {
            child_box = clip_box;
        }
        if (is_error(error_status))
        {
            return optional<Imath::Box2d>();
        }
        if (child_box)
        {
            if (found_first_child)
            {
                box->extendBy(*child_box);
            }
            else
            {
                box               = child_box;
                found_first_child = true;
            }
        }
    }
    return box;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
