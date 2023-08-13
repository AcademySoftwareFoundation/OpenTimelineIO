// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <iostream>

#include "opentimelineio/editAlgorithm.h"

#include "opentimelineio/gap.h"

namespace otime = opentime::OPENTIME_VERSION;

using otime::RationalTime;
using otime::TimeRange;

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


namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

void
edit_slice(
    Composition*        composition,
    RationalTime const& time,
    ErrorStatus*        error_status)
{
    // Find the item to slice.
    auto item = dynamic_retainer_cast<Item>(
        composition->child_at_time(time, error_status, true));
    if (!item)
    {
        return;
    }
    const int       index = composition->index_of_child(item);
    const TimeRange range = composition->trimmed_range_of_child_at_index(index);
                        
    // Adjust the source range for the first slice.
    const TimeRange first_source_range(
        item->trimmed_range().start_time(),
        time - range.start_time());
    item->set_source_range(first_source_range);

    // Clone the item for the second slice.
    auto            second_item = dynamic_cast<Item*>(item->clone());
    const TimeRange second_source_range(
        first_source_range.start_time() + first_source_range.duration(),
        range.duration() - first_source_range.duration());
    second_item->set_source_range(second_source_range);
    composition->insert_child(static_cast<int>(index) + 1, second_item);
}

void
edit_overwrite(
    Item*            item,
    Composition*     composition,
    TimeRange const& range,
    ErrorStatus*     error_status)
{
    const TimeRange composition_range = composition->trimmed_range();
    if (range.start_time() >= composition_range.end_time_exclusive())
    {
        // Append the item and a possible gap.
        const RationalTime gap_duration =
            range.start_time() - composition_range.end_time_exclusive();
        if (gap_duration.value() > 0.0)
        {
            auto gap = new Gap(TimeRange(
                RationalTime(0.0, gap_duration.rate()),
                gap_duration));
            composition->append_child(gap);
        }
        composition->append_child(item);
    }
    else
    {
        // Find the items to overwrite.
        auto items =
            composition->find_children<Item>(error_status, range, true);
        TimeRange item_range =
            composition->trimmed_range_of_child(items.front()).value();
        if (1 == items.size() && item_range.contains(range))
        {
            // The item overwrites a portion inside an item.
            const RationalTime first_duration =
                range.start_time() - item_range.start_time();
            const RationalTime second_duration =
                item_range.duration() - range.duration() - first_duration;
            auto second_item  = dynamic_cast<Item*>(items.front()->clone());
            int  insert_index = composition->index_of_child(items.front()) + 1;
            TimeRange trimmed_range = items.front()->trimmed_range();
            TimeRange source_range(trimmed_range.start_time(), first_duration);
            items.front()->set_source_range(source_range);
            ++insert_index;
            composition->insert_child(insert_index, item);
            ++insert_index;
            trimmed_range = second_item->trimmed_range();
            source_range =
                TimeRange(trimmed_range.start_time(), second_duration);
            second_item->set_source_range(source_range);
            composition->insert_child(insert_index, second_item);
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
edit_insert(
    Item*            insert_item,
    Composition*     composition,
    RationalTime const& time,
    ErrorStatus*     error_status)
{
    // Find the item to split.
    auto item = dynamic_retainer_cast<Item>(
        composition->child_at_time(time, error_status, true));
    if (!item)
    {
        composition->append_child(insert_item);
        return;
    }
    
    const int       index = composition->index_of_child(item);
    const TimeRange range = composition->trimmed_range_of_child_at_index(index);
    int insert_index = index;

    // Adjust the source range for the first slice.
    const TimeRange first_source_range(
        item->trimmed_range().start_time(),
        time - range.start_time());
        
    auto            third_item = dynamic_cast<Item*>(item->clone());
    if (item->trimmed_range().start_time() < time)
    {
        item->set_source_range(first_source_range);
        ++insert_index;
    }

    composition->insert_child(insert_index, insert_item);
    const TimeRange insert_range = composition->trimmed_range_of_child_at_index(insert_index);
    
    // Clone the item for the second slice.
    if (item->trimmed_range().start_time() < time)
    {
        const TimeRange third_source_range(
            insert_range.start_time() + insert_range.duration(),
            range.end_time_exclusive() - time);
        third_item->set_source_range(third_source_range);
        composition->insert_child(insert_index + 1, third_item);
    }
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
