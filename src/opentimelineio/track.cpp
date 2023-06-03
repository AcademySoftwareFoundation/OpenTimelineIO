// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/track.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/gap.h"
#include "opentimelineio/transition.h"
#include "opentimelineio/vectorIndexing.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Track::Track(
    std::string const&         name,
    optional<TimeRange> const& source_range,
    std::string const&         kind,
    AnyDictionary const&       metadata)
    : Parent(name, source_range, metadata)
    , _kind(kind)
{}

Track::~Track()
{}

std::string
Track::composition_kind() const
{
    static std::string kind = "Track";
    return kind;
}

bool
Track::read_from(Reader& reader)
{
    return reader.read("kind", &_kind) && Parent::read_from(reader);
}

void
Track::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("kind", _kind);
}

TimeRange
Track::range_of_child_at_index(int index, ErrorStatus* error_status) const
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

    Composable*  child          = children()[index];
    RationalTime child_duration = child->duration(error_status);
    if (is_error(error_status))
    {
        return TimeRange();
    }

    RationalTime start_time(0, child_duration.rate());

    for (int i = 0; i < index; i++)
    {
        Composable* child2 = children()[i];
        if (!child2->overlapping())
        {
            start_time += children()[i]->duration(error_status);
        }
        if (is_error(error_status))
        {
            return TimeRange();
        }
    }

    if (auto transition = dynamic_cast<Transition*>(child))
    {
        start_time -= transition->in_offset();
    }

    return TimeRange(start_time, child_duration);
}

TimeRange
Track::trimmed_range_of_child_at_index(int index, ErrorStatus* error_status)
    const
{
    auto child_range = range_of_child_at_index(index, error_status);
    if (is_error(error_status))
    {
        return child_range;
    }

    auto trimmed_range = trim_child_range(child_range);
    if (!trimmed_range)
    {
        if (error_status)
        {
            *error_status = ErrorStatus::INVALID_TIME_RANGE;
        }
        return TimeRange();
    }

    return *trimmed_range;
}

TimeRange
Track::available_range(ErrorStatus* error_status) const
{
    RationalTime duration;
    for (const auto& child: children())
    {
        if (auto item = dynamic_retainer_cast<Item>(child))
        {
            duration += item->duration(error_status);
            if (is_error(error_status))
            {
                return TimeRange();
            }
        }
    }

    if (!children().empty())
    {
        if (auto transition =
                dynamic_retainer_cast<Transition>(children().front()))
        {
            duration += transition->in_offset();
        }
        if (auto transition =
                dynamic_retainer_cast<Transition>(children().back()))
        {
            duration += transition->out_offset();
        }
    }

    return TimeRange(RationalTime(0, duration.rate()), duration);
}

std::pair<optional<RationalTime>, optional<RationalTime>>
Track::handles_of_child(Composable const* child, ErrorStatus* error_status)
    const
{
    optional<RationalTime> head, tail;
    auto                   neighbors = neighbors_of(child, error_status);
    if (auto transition = dynamic_retainer_cast<Transition>(neighbors.first))
    {
        head = transition->in_offset();
    }
    if (auto transition = dynamic_retainer_cast<Transition>(neighbors.second))
    {
        tail = transition->out_offset();
    }
    return std::make_pair(head, tail);
}

std::pair<Composable::Retainer<Composable>, Composable::Retainer<Composable>>
Track::neighbors_of(
    Composable const* item,
    ErrorStatus*      error_status,
    NeighborGapPolicy insert_gap) const
{
    std::pair<Retainer<Composable>, Retainer<Composable>> result{ nullptr,
                                                                  nullptr };

    auto index = _index_of_child(item, error_status);
    if (is_error(error_status))
    {
        return result;
    }

    if (index == 0)
    {
        if (insert_gap == NeighborGapPolicy::around_transitions)
        {
            if (auto transition = dynamic_cast<Transition const*>(item))
            {
                result.first = new Gap(TimeRange(
                    // fetch the rate from the offset on the transition
                    RationalTime(0, transition->in_offset().rate()),
                    transition->in_offset()));
            }
        }
    }
    else
    {
        result.first = children()[index - 1];
    }

    if (index == int(children().size()) - 1)
    {
        if (insert_gap == NeighborGapPolicy::around_transitions)
        {
            if (auto transition = dynamic_cast<Transition const*>(item))
            {
                result.second = new Gap(TimeRange(
                    // fetch the rate from the offset on the transition
                    RationalTime(0, transition->out_offset().rate()),
                    transition->out_offset()));
            }
        }
    }
    else
    {
        result.second = children()[index + 1];
    }

    return result;
}

std::map<Composable*, TimeRange>
Track::range_of_all_children(ErrorStatus* error_status) const
{
    std::map<Composable*, TimeRange> result;
    if (children().empty())
    {
        return result;
    }

    auto   first_child = children().front();
    double rate        = 1;

    if (auto transition = dynamic_retainer_cast<Transition>(first_child))
    {
        rate = transition->in_offset().rate();
    }
    else if (auto item = dynamic_retainer_cast<Item>(first_child))
    {
        rate = item->trimmed_range(error_status).duration().rate();
        if (is_error(error_status))
        {
            return result;
        }
    }

    RationalTime last_end_time(0, rate);
    for (const auto& child: children())
    {
        if (auto transition = dynamic_retainer_cast<Transition>(child))
        {
            result[child] = TimeRange(
                last_end_time - transition->in_offset(),
                transition->out_offset() + transition->in_offset());
        }
        else if (auto item = dynamic_retainer_cast<Item>(child))
        {
            auto last_range = TimeRange(
                last_end_time,
                item->trimmed_range(error_status).duration());
            result[child] = last_range;
            last_end_time = last_range.end_time_exclusive();
        }

        if (is_error(error_status))
        {
            return result;
        }
    }

    return result;
}

std::vector<SerializableObject::Retainer<Clip>>
Track::find_clips(
    ErrorStatus*               error_status,
    optional<TimeRange> const& search_range,
    bool                       shallow_search) const
{
    return find_children<Clip>(error_status, search_range, shallow_search);
}

optional<IMATH_NAMESPACE::Box2d>
Track::available_image_bounds(ErrorStatus* error_status) const
{
    optional<IMATH_NAMESPACE::Box2d> box;
    bool                   found_first_clip = false;
    for (const auto& child: children())
    {
        if (auto clip = dynamic_cast<Clip*>(child.value))
        {
            if (auto clip_box = clip->available_image_bounds(error_status))
            {
                if (clip_box)
                {
                    if (found_first_clip)
                    {
                        box->extendBy(*clip_box);
                    }
                    else
                    {
                        box              = clip_box;
                        found_first_clip = true;
                    }
                }
            }
            if (is_error(error_status))
            {
                return optional<IMATH_NAMESPACE::Box2d>();
            }
        }
    }
    return box;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
