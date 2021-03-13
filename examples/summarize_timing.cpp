// Example OTIO program that reads a timeline and then prints a summary
// of the video clips found, including re-timing effects on each one.

#include "util.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/freezeFrame.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/linearTimeWarp.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/transition.h>

#include <iostream>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
namespace otime = opentime::OPENTIME_VERSION;

void _summarize_effects(const otio::Item* item)
{
    for (auto effect : item->effects())
    {
        if (auto freezeFrame = dynamic_cast<otio::FreezeFrame*>(effect.value))
        {
            std::cout << "Effect: Freeze Frame" << std::endl;
        }
        else if (auto linearTimeWarp = dynamic_cast<otio::LinearTimeWarp*>(effect.value))
        {
            std::cout.precision(2);
            std::cout << "Effect: Linear Time Warp (" << std::fixed <<
                linearTimeWarp->time_scalar() * 100.0 << "%)" << std::endl;
        }
        else
        {
            std::cout << "Effect: " << effect.value->name() <<
                "(" << typeid(effect.value).name() << ")" << std::endl;
        }
    }
}

void _summarize_range(std::string const& label, otio::TimeRange const& time_range, otio::ErrorStatus const& errorStatus)
{
    if (errorStatus.outcome != otio::ErrorStatus::Outcome::OK)
    {
        std::cout << '\t' << label << ": None" << std::endl;
    }
    else
    {
        otime::ErrorStatus otimeErrorStatus;
        std::cout << '\t' << label << ": " <<
            time_range.start_time().to_timecode(&otimeErrorStatus) << " - " <<
            time_range.end_time_exclusive().to_timecode(&otimeErrorStatus) <<
            " (Duration: " << time_range.duration().to_timecode(&otimeErrorStatus) << ")" << std::endl;
    }
}

void _summarize_timeline(const otio::Timeline* timeline)
{
    // Here we iterate over each video track, and then just the top-level
    // items in each track.
    // See also: https://opentimelineio.readthedocs.io/en/latest/tutorials/otio-timeline-structure.html  # noqa
    for (const auto i : timeline->tracks()->children())
    {
        if (auto track = dynamic_cast<otio::Track*>(i.value))
        {
            otio::ErrorStatus errorStatus;
            std::cout << "Track: " << track->name() << '\n' <<
                "\tKind: " << track->kind() << '\n' <<
                "\tDuration: " << track->duration(&errorStatus).to_time_string() << std::endl;
            _summarize_effects(track);
            
            for (auto child : track->children())
            {
                if (auto item = dynamic_cast<otio::Item*>(child.value))
                {
                    if (auto clip = dynamic_cast<otio::Clip*>(item))
                    {
                        std::cout << "Clip: " << clip->name() << std::endl;
                        // See the documentation to understand the difference
                        // between each of these ranges:
                        // https://opentimelineio.readthedocs.io/en/latest/tutorials/time-ranges.html
                        _summarize_range("  Trimmed Range", clip->trimmed_range(&errorStatus), errorStatus);
                        _summarize_range("  Visible Range", clip->visible_range(&errorStatus), errorStatus);
                        _summarize_range("Available Range", clip->available_range(&errorStatus), errorStatus);
                    }
                    else if (auto gap = dynamic_cast<otio::Gap*>(item))
                    {
                        continue;
                    }
                    else if (auto transition = dynamic_cast<otio::Transition*>(item))
                    {
                        otime::ErrorStatus otimeErrorStatus;
                        std::cout << "Transition: " << transition->transition_type() << '\n' <<
                            "\tDuration: " << transition->duration(&errorStatus).to_timecode(&otimeErrorStatus) << std::endl;
                    }
                    else if (auto composition = dynamic_cast<otio::Composition*>(item))
                    {
                        std::cout << "Nested Composition: " << composition->name() << '\n' <<
                            "\tDuration: " << composition->duration(&errorStatus).to_time_string() << std::endl;
                    }
                    else
                    {
                        std::cout << "Other: " << item->name() << "(" << typeid(item).name() << ")" << '\n' <<
                            "\tDuration: " << item->duration(&errorStatus).to_time_string() << std::endl;
                    }
                    _summarize_effects(item);
                }
            }
        }
    }
}

int main(int argc, char** argv)
{
    PythonAdapters adapters;
    for (int i = 1; i < argc; ++i)
    {
        otio::ErrorStatus error_status;
        auto timeline = adapters.read_from_file(argv[i], &error_status);
        if (!timeline)
        {
            print_error(error_status);
            return 1;
        }
        
        _summarize_timeline(timeline);
    }
    return 0;
}

