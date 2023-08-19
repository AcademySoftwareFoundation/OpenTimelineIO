// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <iostream>

#include "opentimelineio/algo/editAlgorithm.h"

#include "opentimelineio/gap.h"
#include "opentimelineio/linearTimeWarp.h"
#include "opentimelineio/track.h"
#include "opentimelineio/transition.h"

namespace otime = opentime::OPENTIME_VERSION;

using otime::RationalTime;
using otime::TimeRange;

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace algo {


#include <iostream>


std::ostream& operator << (std::ostream& os, const RationalTime& value)
{
    os << std::fixed << value.value() << "/" << value.rate();
    return os;
}

std::ostream& operator << (std::ostream& os, const TimeRange& value)
{
    os << std::fixed << value.start_time().value() << "/" <<
        value.duration().value() << "/" <<
        value.duration().rate();
    return os;
}

namespace
{

inline std::vector<SerializableObject::Retainer<Item>>
find_items_in_composition(
    Composition*        composition,
    RationalTime const& time,
    ErrorStatus*        error_status)
{
    // Find the item to slice.
    TimeRange search_range(time, RationalTime(1.0, time.rate()));
    return composition->find_children<Item>(error_status, search_range, true);
}

} // namespace

void
overwrite(
    Item*            item,
    Composition*     composition,
    TimeRange const& range,
    bool const       remove_transitions,
    Item*            fill_template,
    ErrorStatus*     error_status)
{
    const TimeRange composition_range = composition->trimmed_range();
    if (range.start_time() >= composition_range.end_time_exclusive())
    {
        // Append the item and a possible fill (gap).
        const RationalTime fill_duration =
            range.start_time() - composition_range.end_time_exclusive();
        if (fill_duration.value() > 0.0)
        {
            const TimeRange fill_range = TimeRange(
                RationalTime(0.0, fill_duration.rate()),
                fill_duration);
            if (!fill_template)
                fill_template = new Gap(fill_range);
            else
                fill_template->set_source_range(fill_range);
            composition->append_child(fill_template);
        }
        composition->append_child(item);
    }
    else
    {
        // Check for transitions to remove first.
        if (remove_transitions)
        {
            auto transitions = composition->find_children<Transition>(
                error_status,
                range,
                true);
            if (!transitions.empty())
            {
                for (const auto& transition : transitions)
                {
                    int index = composition->index_of_child(transition);
                    if (index < 0 || index >= composition->children().size())
                        continue;
                    composition->remove_child(transition);
                }
            }
        }

        // Find the items to overwrite.
        auto items =
            composition->find_children<Item>(error_status, range, true);
        TimeRange item_range =
            composition->trimmed_range_of_child(items.front()).value();
        if (1 == items.size() && item_range.contains(range, 0.0))
        {
            // The item overwrites a portion inside an item.
            const RationalTime first_duration =
                range.start_time() - item_range.start_time();
            const RationalTime second_duration =
                item_range.duration() - range.duration() - first_duration;
            int insert_index = composition->index_of_child(items.front()) + 1;
            TimeRange trimmed_range = items.front()->trimmed_range();
            TimeRange source_range(trimmed_range.start_time(), first_duration);
            if (first_duration.value() <= 0.0)
            {
                --insert_index;
                composition->remove_child(insert_index);
            }
            else
            {
                auto first_item = items.front();
                first_item->set_source_range(source_range);
                ++insert_index;
            }
            composition->insert_child(insert_index, item);
            if (second_duration.value() > 0.0)
            {
                auto second_item = dynamic_cast<Item*>(items.front()->clone());
                trimmed_range    = second_item->trimmed_range();
                source_range     = TimeRange(
                    trimmed_range.start_time() + first_duration
                        + range.duration(),
                    second_duration);
                ++insert_index;
                second_item->set_source_range(source_range);
                composition->insert_child(insert_index, second_item);
            }
        }
        else
        {
            // Determine if the first item is partially overwritten.
            int       insert_index = composition->index_of_child(items.front());
            bool      first_partial = false;
            TimeRange first_source_range;
            if (item_range.start_time() < range.start_time())
            {
                first_partial                 = true;
                const TimeRange trimmed_range = items.front()->trimmed_range();
                first_source_range            = TimeRange(
                    trimmed_range.start_time(),
                    range.start_time() - item_range.start_time());
                ++insert_index;
            }

            // Determine if the last item is partially overwritten.
            bool      last_partial = false;
            TimeRange last_source_range;
            if (items.size() > 1)
            {
                item_range =
                    composition->trimmed_range_of_child(items.back()).value();
                if (item_range.end_time_inclusive()
                    > range.end_time_inclusive())
                {
                    last_partial = true;
                    const TimeRange trimmed_range =
                        items.back()->trimmed_range();
                    const RationalTime duration =
                        item_range.end_time_inclusive()
                        - range.end_time_inclusive();
                    last_source_range = TimeRange(
                        trimmed_range.start_time() + duration,
                        trimmed_range.duration() - duration);
                }
            }

            // Adjust the first and last items.
            if (first_partial)
            {
                items.front()->set_source_range(first_source_range);
                items.erase(items.begin());
            }
            if (last_partial)
            {
                items.back()->set_source_range(last_source_range);
                items.erase(items.end() - 1);
            }

            // Remove the completely overwritten items.
            while (!items.empty())
            {
                composition->remove_child(items.back());
                items.pop_back();
            }

            // Insert the item.
            const TimeRange trimmed_range = item->trimmed_range();
            item->set_source_range(
                TimeRange(trimmed_range.start_time(), range.duration()));
            composition->insert_child(insert_index, item);
        }
    }
}

void
insert(
    Item*            insert_item,
    Composition*     composition,
    RationalTime const& time,
    bool const       remove_transitions,
    Item*            fill_template,
    ErrorStatus*     error_status)
{
    // Check for transitions to remove first.
    if (remove_transitions)
    {
        TimeRange range(time, RationalTime(1.0, time.rate()));
        auto transitions = composition->find_children<Transition>(
            error_status,
            range,
            true);
        if (!transitions.empty())
        {
            for (const auto& transition : transitions)
            {
                int index = composition->index_of_child(transition);
                if (index < 0 || index >= composition->children().size())
                    continue;
                composition->remove_child(transition);
            }
        }
    }

    // Find the item to insert into.
    auto items = find_items_in_composition(composition, time, error_status);
    if (items.empty())
    {
        const TimeRange composition_range = composition->trimmed_range();
        if (time >= composition_range.end_time_exclusive())
        {
            // Append the item and a possible fill (gap).
            const RationalTime fill_duration =
                time - composition_range.end_time_exclusive();
            if (fill_duration.value() > 0.0)
            {
                const TimeRange fill_range = TimeRange(
                    RationalTime(0.0, fill_duration.rate()),
                    fill_duration);
                if (!fill_template)
                    fill_template = new Gap(fill_range);
                else
                    fill_template->set_source_range(fill_range);
                composition->append_child(fill_template);
            }
            composition->append_child(insert_item);
        }
        else if (time < composition_range.start_time())
            composition->insert_child(0, insert_item);
        return;
    }
    if (items.size() > 1)
    {
        if (error_status)
            *error_status = ErrorStatus::INTERNAL_ERROR;
        return;
    }
    auto item = items.front();

    const int       index = composition->index_of_child(item);
    const TimeRange range = composition->trimmed_range_of_child_at_index(index);
    int insert_index = index;

    // Item is partially split
    const bool split = range.start_time() < time;
    if (split)
    {
        const TimeRange first_source_range(
            item->trimmed_range().start_time(),
            time - range.start_time());
        item->set_source_range(first_source_range);
        ++insert_index;
    }

    // Insert the new item
    composition->insert_child(insert_index, insert_item);
    const TimeRange insert_range = composition->trimmed_range_of_child_at_index(insert_index);

    // Second item from splitting item
    if (split)
    {
        const TimeRange second_source_range(
            insert_range.start_time() + insert_range.duration(),
            range.end_time_exclusive() - time);
        // Clone the item for the second partially overwritten item.
        auto            second_item = dynamic_cast<Item*>(item->clone());
        second_item->set_source_range(second_source_range);
        composition->insert_child(insert_index + 1, second_item);
    }
}

void trim(
    Item*            item,
    RationalTime const& delta_in,
    RationalTime const& delta_out,
    Item*            fill_template,
    ErrorStatus*     error_status)
{
    Composition* composition = item->parent();
    auto children = composition->children();
    const int       index = composition->index_of_child(item);
    
    const TimeRange range = item->trimmed_range();
    RationalTime start_time = range.start_time();
    RationalTime end_time_exclusive = range.end_time_exclusive();
    if (delta_in.value() != 0.0)
    {
        start_time += delta_in;
        if (index > 0)
        {
            auto previous = dynamic_retainer_cast<Item>(children[index - 1]);
            TimeRange previous_range = previous->trimmed_range();
            previous_range = TimeRange(previous_range.start_time(),
                                       previous_range.duration() + delta_in);
            previous->set_source_range(previous_range);
        }
    }
    if (delta_out.value() != 0.0)
    {
        const size_t next_index = index + 1;
        if (next_index < children.size())
        {
            auto next = dynamic_retainer_cast<Item>(children[next_index]);
            auto gap_next = dynamic_retainer_cast<Gap>(children[next_index]);
            if (gap_next && delta_out.value() > 0.0)
            {
                end_time_exclusive += delta_out;
            }
            else if (delta_out.value() < 0.0)
            {
                if (gap_next)
                {
                    end_time_exclusive += delta_out;
                    const TimeRange gap_range = gap_next->trimmed_range();
                    const TimeRange gap_new_range(
                        gap_range.start_time() - delta_out,
                        gap_range.duration() + delta_out);
                    gap_next->set_source_range(gap_new_range);
                }
                else
                {
                    end_time_exclusive += delta_out;

                    const RationalTime fill_duration = -delta_out;
                    if (fill_duration.value() > 0.0)
                    {
                        const TimeRange fill_range = TimeRange(
                            RationalTime(0.0, fill_duration.rate()),
                            fill_duration);
                        if (!fill_template)
                            fill_template = new Gap(fill_range);
                        else
                            fill_template->set_source_range(fill_range);
                        composition->insert_child(next_index, fill_template);
                    }
                }
            }
        }
    }
    const TimeRange new_range =
        TimeRange::range_from_start_end_time(start_time, end_time_exclusive);
    item->set_source_range(new_range);
}

void
slice(
    Composition*        composition,
    RationalTime const& time,
    bool const          remove_transitions,
    ErrorStatus*        error_status)
{
    auto items = find_items_in_composition(composition, time, error_status);
    if (items.empty())
    {
        if (error_status)
            *error_status = ErrorStatus::NOT_AN_ITEM;
        return;
    }
    if (items.size() > 1)
    {
        if (error_status)
            *error_status = ErrorStatus::INTERNAL_ERROR;
        return;
    }
    auto item = items.front();
        
    const int       index = composition->index_of_child(item);
    const TimeRange range = composition->trimmed_range_of_child_at_index(index);

    
    // Check for slice at start of clip (invalid slice)
    const RationalTime duration = time - range.start_time();
    if (duration.value() <= 0.0)
        return;
    
    // Accumulate intersecting transitions
    std::vector<Transition*> transitions;
    if (auto track = dynamic_cast<Track*>(composition))
    {
        const auto neighbors = track->neighbors_of(item, error_status);
        if (auto transition = dynamic_cast<Transition*>(neighbors.second.value))
        {
            const auto transition_range =
                track->trimmed_range_of_child(transition).value();
            if (transition_range.contains(time))
            {
                transitions.push_back(transition);
            }
        }
        if (auto transition = dynamic_cast<Transition*>(neighbors.first.value))
        {
            const auto transition_range =
                track->trimmed_range_of_child(transition).value();
            if (transition_range.contains(time))
            {
                transitions.push_back(transition);
            }
        }
    }
    
    // Remove transitions
    if (!transitions.empty())
    {
        if (remove_transitions)
        {
            for (auto transition : transitions)
            {
                const int index = composition->index_of_child(transition);
                composition->remove_child(index);
            }
        }
        else
        {
            if (error_status)
                *error_status = ErrorStatus::CANNOT_TRIM_TRANSITION;
            return;
        }
    }
    
    // Adjust the source range for the first slice.
    const TimeRange first_source_range(
        item->trimmed_range().start_time(),
        duration);
    item->set_source_range(first_source_range);

    // Clone the item for the second slice.
    auto            second_item = dynamic_cast<Item*>(item->clone());
    const TimeRange second_source_range(
        first_source_range.start_time() + first_source_range.duration(),
        range.duration() - first_source_range.duration());
    second_item->set_source_range(second_source_range);
    composition->insert_child(static_cast<int>(index) + 1, second_item);
}
            
void slip(
    Item*            item,
    RationalTime const& delta)
{
    const TimeRange range = item->trimmed_range();
    RationalTime start_time = range.start_time();
    start_time += delta;

    // Clamp to available range of media if present
    const TimeRange  available_range = item->available_range();
    if (available_range.duration().value() > 0.0)
    {
        if (start_time < available_range.start_time())
        {
            start_time = available_range.start_time();
        }
        else if (start_time + range.duration() >
                 available_range.end_time_exclusive())
        {
            //     S---E (move <- source start time so that E matches)
            // A-----E
            const RationalTime end_diff = start_time + range.duration() -
                                          available_range.end_time_exclusive();
            start_time -= end_diff;
        }
    }
        
    const TimeRange new_range(start_time, range.duration());
    item->set_source_range(new_range);
}


void slide(
    Item*            item,
    RationalTime const& delta)
{
    Composition* composition = item->parent();
    const int       index = composition->index_of_child(item);

    // Exit early if we are at the first clip or if the delta is 0.
    if (index <= 0 || delta.value() == 0.0F)
    {
        return;
    }
    
    auto children = composition->children();
    auto previous = dynamic_retainer_cast<Item>(children[index - 1]);
    const TimeRange range = previous->trimmed_range();
    const TimeRange available_range = previous->available_range();
    RationalTime offset = delta;

    if (delta.value() < 0)
    {
        // Check we don't move left beyond the previous clip's duration
        if (range.duration() <= -delta)
        {
            return;
        }
    }
    else
    {
        // Check we don't move right beyond the previous clip's
        // available duration
        if (available_range.duration().value() > 0.0 &&
            range.duration() + delta > available_range.duration())
        {
            offset = available_range.duration() - range.duration();
        }
    }
    
    const otime::TimeRange new_range(range.start_time(),
                                     range.duration() + offset);
    previous->set_source_range(new_range);
}

void ripple(
    Item*            item,
    RationalTime const& delta_in,
    RationalTime const& delta_out,
    ErrorStatus*     error_status)
{
    const TimeRange range = item->trimmed_range();
    RationalTime start_time = range.start_time();
    RationalTime end_time_exclusive = range.end_time_exclusive();
    if (delta_in.value() != 0.0)
    {
        RationalTime in_offset = delta_in;
        if (delta_in < start_time)
        {
            in_offset = -start_time;
        }
        else if (start_time + delta_in > end_time_exclusive)
        {
            in_offset = delta_in - end_time_exclusive;
        }
        start_time += in_offset;
    }
    if (delta_out.value() != 0.0)
    {
        RationalTime out_offset = delta_out;
        if (delta_out.value() > 0.0)
        {
            const TimeRange available_range = item->available_range();

            // Check we don't move right beyond the clip's
            // available duration
            if (available_range.duration().value() > 0.0 &&
                range.duration() + delta_out > available_range.duration())
            {
                out_offset = available_range.duration() - range.duration();
            }
        }

        end_time_exclusive += out_offset;
    }
    const TimeRange new_range =
        TimeRange::range_from_start_end_time(start_time, end_time_exclusive);
    item->set_source_range(new_range);
}

void
roll(
    Item*               item,
    RationalTime const& delta_in,
    RationalTime const& delta_out,
    ErrorStatus*        error_status)
{
    Composition* composition = item->parent();
    auto children = composition->children();
    const int       index = composition->index_of_child(item);
    
    const TimeRange range = item->trimmed_range();
    const TimeRange available_range = item->available_range();
    RationalTime start_time = range.start_time();
    RationalTime end_time_exclusive = range.end_time_exclusive();
    if (delta_in.value() != 0.0)
    {
        const RationalTime available_start_time = available_range.start_time();
        RationalTime in_offset = delta_in;
        if (-in_offset > start_time)
            in_offset = -start_time;
        if (index > 0)
        {
            auto previous = dynamic_retainer_cast<Item>(children[index - 1]);
            TimeRange previous_range = previous->trimmed_range();

            // Clamp to previous clip's range first
            RationalTime duration = previous_range.duration();
            if (duration < -in_offset)
            {
                duration -= RationalTime(1.0, duration.rate());
                in_offset -= duration; 
            }
            previous_range = TimeRange(previous_range.start_time(),
                                       previous_range.duration() + in_offset);
            previous->set_source_range(previous_range);
        }
        start_time += in_offset;

        // If available range present, clamp to its start_time.
        if (available_range.duration().value() > 0.0)
        {
            if (start_time < available_start_time)
                start_time = available_start_time;
        }
    }
    if (delta_out.value() != 0.0)
    {
        const size_t next_index = index + 1;
        if (next_index < children.size())
        {
            auto next = dynamic_retainer_cast<Item>(children[next_index]);
            TimeRange next_range = next->trimmed_range();
            const TimeRange available_range = next->available_range();
            RationalTime next_start_time = next_range.start_time();
            RationalTime out_offset = delta_out;

            // If avalable range, clamp to it.
            if (available_range.duration().value() > 0.0)
            {
                RationalTime available_start_time =
                    available_range.start_time();
                if (-out_offset > available_start_time)
                    out_offset = -available_start_time;
            }
            else
            {
                if (-out_offset > next_start_time)
                    out_offset = -next_start_time;
            }
        
            end_time_exclusive += out_offset;
            next_start_time    += out_offset;
            next_range = TimeRange(next_start_time,
                                   next_range.duration());
            next->set_source_range(next_range);
        }
    }
    const TimeRange new_range =
        TimeRange::range_from_start_end_time(start_time, end_time_exclusive);
    item->set_source_range(new_range);
}

void
fill(
    Item*                item,
    Composition*         track,
    RationalTime const&  track_time,
    ReferencePoint const reference_point,
    ErrorStatus*         error_status)
{
    // Find the gap to replace.
    auto gap = dynamic_retainer_cast<Gap>(
        track->child_at_time(track_time, error_status, true));
    if (!gap)
    {
        if (error_status)
            *error_status = ErrorStatus::NOT_A_GAP;
        return;
    }

    const TimeRange clip_range       = item->trimmed_range();
    const TimeRange gap_range        = gap->trimmed_range();
    TimeRange gap_track_range = track->trimmed_range_of_child(gap).value();
    RationalTime duration   = clip_range.duration();

    switch (reference_point)
    {
        case ReferencePoint::Sequence: {
            RationalTime start_time = clip_range.start_time();
            const RationalTime gap_start_time = gap_range.start_time();
            auto         track_item = dynamic_cast<Item*>(item->clone());

            // Check if start time is less than gap's start time (trim it if so)
            if (start_time < gap_start_time)
            {
                duration -= gap_start_time - start_time;
                start_time = gap_start_time;
            }
            
            // Check if end time is longer (trim it if it is)
            if (clip_range.end_time_exclusive()
                > gap_range.end_time_exclusive())
            {
                duration = gap_range.end_time_exclusive() - start_time;
            }
            const TimeRange new_clip_range(start_time, duration);
            track_item->set_source_range(new_clip_range);

            if (duration
                > gap_track_range.end_time_exclusive() - track_time)
            {
                duration =
                    gap_track_range.end_time_exclusive() - track_time;
            }
            
            const TimeRange time_range(track_time, duration);
            overwrite(
                track_item,
                track,
                time_range,
                true,
                nullptr,
                error_status);
            return;
        }

        case ReferencePoint::Fit: {
            const double pct = gap_range.duration().to_seconds()
                               / duration.to_seconds();
            const std::string& name = item->name();
            LinearTimeWarp* timeWarp =
                new LinearTimeWarp(name, name + "_timeWarp", pct);
            std::vector<Effect*> effects;
            effects.push_back(timeWarp);
            item = new Item(name, clip_range, AnyDictionary(), effects);
            const TimeRange time_range(
                track_time,
                gap_track_range.end_time_exclusive() - track_time);
            overwrite(item, track, time_range, true, nullptr, error_status);
            return;
        }

        case ReferencePoint::Source:
        default: {
            const TimeRange time_range(track_time, duration);
            overwrite(item, track, time_range, true, nullptr, error_status);
            return;
        }
    };
}

}}} // namespace opentimelineio::OPENTIMELINEIO_VERSION::algo
