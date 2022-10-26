// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/trackAlgorithm.h"
#include "opentimelineio/transition.h"
#include "opentimelineio/linearTimeWarp.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

static double _compute_time_scalar(Item* item)
{
    double time_scalar = 1.0;

    for (const auto& effect : item->effects())
    {
        // Note: FreezeFrame is handled here because it is a subclass of
        // LinearTimeWarp. However, generic TimeEffect is not, since non-linear
        // warps cannot be decomposed into a simple scalar value. Non-linear
        // warps are simply ignored here and left for future development.
        if (const auto linear_time_warp =
                dynamic_cast<LinearTimeWarp*>(effect.value)) {
            time_scalar *= linear_time_warp->time_scalar();
        }
    }

    return time_scalar;
}

static void _snap_timewarps(Item* item)
{
    int item_frames = item->duration().to_frames();
    auto range = item->trimmed_range();
    // snap the item's start time to whole frames
    item->set_source_range(
       TimeRange(RationalTime(range.start_time().to_frames(),
                              range.start_time().rate()),
                 range.duration()));

    for (const auto& effect : item->effects())
    {
        if (const auto linear_time_warp =
                dynamic_cast<LinearTimeWarp*>(effect.value)) {
            // TODO: What happens with FreezeFrame here?
            // snap the time_scalar to be a rational number
            double time_scalar = linear_time_warp->time_scalar();
            int media_frames = rint(item_frames * time_scalar);
            time_scalar = (double)media_frames / item_frames;
            linear_time_warp->set_time_scalar(time_scalar);
        }
    }
}

// TODO: SnappedLinearTimeWarp???

Track*
track_trimmed_to_range(
    Track*       in_track,
    TimeRange    trim_range,
    ErrorStatus* error_status,
    TrimPolicy   trimPolicy)
{
    Track* new_track = dynamic_cast<Track*>(in_track->clone(error_status));
    if (is_error(error_status) || !new_track)
    {
        return nullptr;
    }

    auto track_map = new_track->range_of_all_children(error_status);
    if (is_error(error_status))
    {
        return nullptr;
    }

    std::vector<Composable*> children_copy(
        new_track->children().begin(),
        new_track->children().end());

    for (size_t i = children_copy.size(); i--;)
    {
        Composable* child          = children_copy[i];
        auto        child_range_it = track_map.find(child);
        if (child_range_it == track_map.end())
        {
            if (error_status)
            {
                *error_status = ErrorStatus(
                    ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
                    "failed to find child in track_map map");
            }
            return nullptr;
        }

        auto child_range = child_range_it->second;
        if (!trim_range.intersects(child_range))
        {
            new_track->remove_child(static_cast<int>(i), error_status);
            if (is_error(error_status))
            {
                return nullptr;
            }
        }
        else if (!trim_range.contains(child_range))
        {
            if (dynamic_cast<Transition*>(child))
            {
                if (error_status)
                {
                    *error_status = ErrorStatus(
                        ErrorStatus::CANNOT_TRIM_TRANSITION,
                        "Cannot trim in the middle of a transition");
                }
                return nullptr;
            }

            Item* child_item = dynamic_cast<Item*>(child);
            if (!child_item)
            {
                if (error_status)
                {
                    *error_status = ErrorStatus(
                        ErrorStatus::TYPE_MISMATCH,
                        "Expected child of type Item*",
                        child);
                }
                return nullptr;
            }
            auto child_source_range = child_item->trimmed_range(error_status);
            if (is_error(error_status))
            {
                return nullptr;
            }

            float time_scalar = 1.0;
            switch (trimPolicy) {
                case HonorTimeEffectsExactly:
                case HonorTimeEffectsWithSnapping:
                    time_scalar = _compute_time_scalar(child_item);
                    break;
                case IgnoreTimeEffects:
                default:
                    break;
            }

            // TODO: What if there are non-linear time warp here?

            // Does the trim start after this child?
            // If so, we need to remove the beginning of the child.
            if (trim_range.start_time() > child_range.start_time())
            {
                auto trim_amount =
                trim_range.start_time() - child_range.start_time();
                auto scaled_trim_amount =
                    RationalTime(trim_amount.value() * time_scalar,
                                 trim_amount.rate());
                child_source_range =
                    TimeRange(child_source_range.start_time() +
                                scaled_trim_amount,
                              child_source_range.duration() - trim_amount);
            }

            // Does the trim end before this child ends?
            // If so, we need to remove the end of the child.
            auto trim_end  = trim_range.end_time_exclusive();
            auto child_end = child_range.end_time_exclusive();
            if (trim_end < child_end)
            {
                auto trim_amount = child_end - trim_end;
                child_source_range =
                TimeRange(
                          child_source_range.start_time(),
                          child_source_range.duration() - trim_amount);
            }

            child_item->set_source_range(child_source_range);
            if (trimPolicy == HonorTimeEffectsWithSnapping) {
                _snap_timewarps(child_item);
            }
        }
    }

    return new_track;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
