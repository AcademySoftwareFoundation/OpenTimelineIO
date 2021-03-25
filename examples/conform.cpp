#include "util.h"

#include <opentimelineio/externalReference.h>
#include <opentimelineio/timeline.h>

#include <iostream>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

otio::optional<std::string> args_input = otio::nullopt;
otio::optional<std::string> args_folder = otio::nullopt;
otio::optional<std::string> args_output = otio::nullopt;

bool parse_args(int argc, char** argv)
{
    if (argc > 1)
    {
        args_input = std::string(argv[1]);
    }
    for (int i = 2; i < argc; ++i)
    {
        const std::string arg(argv[i]);
        if (("-f" == arg || "--folder" == arg) && i < argc - 1)
        {
            ++i;
            args_folder = std::string(argv[i]);
        }
        else if (("-o" == arg || "--output" == arg) && i < argc - 1)
        {
            ++i;
            args_output = std::string(argv[i]);
        }
    }
    return args_input && args_folder && args_output;
}

void print_usage()
{
    std::cout << "Example OTIO program that reads a timeline and then relinks clips" << std::endl;
    std::cout << "to movie files found in a given folder, based on matching names." << std::endl;
    std::cout << std::endl;
    std::cout << "Demo:" << std::endl;
    std::cout << std::endl;
    std::cout << "% ls - 1R" << std::endl;
    std::cout << "editorial_cut.otio" << std::endl;
    std::cout << "media /" << std::endl;
    std::cout << "shot1.mov" << std::endl;
    std::cout << "shot17.mov" << std::endl;
    std::cout << "shot99.mov" << std::endl;
    std::cout << std::endl;
    std::cout << "% conform editorial_cut.otio -f media -o conformed.otio" << std::endl;
    std::cout << "Relinked 3 clips to new media." << std::endl;
    std::cout << "Saved conformed.otio with 100 clips." << std::endl;
    std::cout << std::endl;
    std::cout << "% diff editorial_cut.otio conformed.otio" << std::endl;
}

// Look for media with this name in this folder.
std::string find_matching_media(std::string const& name, std::string const& folder)
{
    // In this case we're looking in the filesystem.
    // In your case, you might want to look in your asset management system
    // and you might want to use studio - specific metadata in the clip instead
    // of just the clip name.
    // Something like this:
    // shot = asset_database.find_shot(clip.metadata['mystudio']['shotID'])
    // new_media = shot.latest_render(format = 'mov')

    auto matches = glob(normalize_path(folder) + '/' + name + ".*");
    std::transform(matches.begin(), matches.end(), matches.begin(), [](std::string const& in) { return absolute_path(in); });

    if (matches.empty())
    {
        // std::cout << "DEBUG: No match for clip '" << name << "'";
        return {};
    }
    if (1 == matches.size())
        return matches[0];
    else
    {
        std::cout << "WARNING: " << matches.size() <<
            " matches found for clip " << name <<
            ", using '" << matches[0] << "'" << std::endl;
        return matches[0];
    }
    return {};
}

// Look for replacement media for each clip in the given timeline.
//
// The clips are relinked in place if media with a matching name is found.
size_t conform_timeline(
    otio::SerializableObject::Retainer<otio::Timeline> const& timeline,
    std::string const& folder,
    otio::ErrorStatus* error_status)
{
    size_t count = 0;

    for (const auto& clip : timeline.value->each_clip(error_status))
    {
        // look for a media file that matches the clip's name
        std::string new_path = find_matching_media(clip.value->name(), folder);

        // if no media is found, keep going
        if (new_path.empty())
            continue;

        // if we found one, then relink to the new path
        clip.value->set_media_reference(new otio::ExternalReference(
            "file://" + new_path,
            otio::nullopt // we don't know the available range
            ));

        count += 1;
    }

    return count;
}

int main(int argc, char** argv)
{
    if (!parse_args(argc, argv))
    {
        print_usage();
        return 1;
    }

    otio::ErrorStatus error_status;
    otio::SerializableObject::Retainer<otio::Timeline> timeline(dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(*args_input, &error_status)));
    if (!timeline)
    {
        print_error(error_status);
        return 1;
    }
    const size_t count = conform_timeline(timeline, *args_folder, &error_status);
    std::cout << "Relinked " << count << " clips to new media." << std::endl;
    if (!timeline.value->to_json_file(*args_output, &error_status))
    {
        print_error(error_status);
        return 1;
    }
    std::cout << "Saved " << *args_output << " with " << timeline.value->each_clip(&error_status).size() << " clips." << std::endl;

    return 0;
}
