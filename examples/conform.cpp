// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

// Example OTIO script that reads a timeline and then relinks clips
// to movie files found in a given folder, based on matching clip names to filenames.
//
// Demo:
//
// % ls -1R
// editorial_cut.otio
// media/
//    shot1.mov
//    shot17.mov
//    shot99.mov
//
// % conform editorial_cut.otio media conformed.otio
// Relinked 3 clips to new media.
// Saved conformed.otio with 100 clips.
//
// % diff editorial_cut.otio conformed.otio
// ...

#include "util.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/fileUtils.h>
#include <opentimelineio/timeline.h>

#include <iostream>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION_NS;

// Look for media with this name in this folder.
std::string find_matching_media(std::string const& name, std::string const& folder)
{
    // This function is an example which searches the file system for matching media.
    // A real world studio implementation would likely look in an asset management system
    // and use studio-specific metadata in the clip's metadata dictionary instead
    // of matching the clip name.
    // For example:
    // shot = asset_database->find_shot(
    //    otio::any_cast<std::map<std::string, std::string> >(clip->metadata()["mystudio"])["shotID"]);
    // new_media = shot->latest_render("mov");
    
    const auto matches = examples::glob(folder, name + ".*");
    
    if (matches.size() == 0)
    {
        //std::cout << "DEBUG: No match for clip '" << name << "'" << std::endl;
        return std::string();
    }
    if (matches.size() == 1)
    {
        return matches[0];
    }
    else
    {
        std::cout << "WARNING: " << matches.size() << " matches found for clip '" <<
            name << "', using '" << matches[0] << "'";
        return matches[0];
    }
}

// Look for replacement media for each clip in the given timeline.
//
// The clips are relinked in place if media with a matching name is found.
//
// Note the use of otio::SerializableObject::Retainer to wrap the timeline,
// it provides a safe way to manage the memory of otio objects by keeping an
// internal reference count. For more details on the usage of Retainers see
// the C++ documentation:
// https://opentimelineio.readthedocs.io/en/latest/cxx/cxx.html
int conform_timeline(
    otio::SerializableObject::Retainer<otio::Timeline> const& timeline,
    std::string const& folder)
{
    int count = 0;
    
    otio::ErrorStatus error_status;
    const auto clips = timeline->find_clips(&error_status);
    if (otio::is_error(error_status))
    {
        examples::print_error(error_status);
        exit(1);
    }
    
    for (const otio::SerializableObject::Retainer<otio::Clip>& clip : clips)
    {
        // look for a media file that matches the clip's name
        const std::string new_path = find_matching_media(clip->name(), folder);

        // if no media is found, keep going
        if (new_path.empty())
            continue;

        // relink to the found path
        clip->set_media_reference(new otio::ExternalReference(
            "file://" + new_path,
            std::nullopt // the available range is unknown without opening the file
        ));
        count += 1;
    }
    
    return count;
}

int main(int argc, char** argv)
{
    if (argc != 4)
    {
        std::cout << "Usage: conform (input) (folder) (output)" << std::endl;
        return 1;
    }
    const std::string input = otio::to_unix_separators(argv[1]);
    const std::string folder = otio::to_unix_separators(argv[2]);
    const std::string output = otio::to_unix_separators(argv[3]);
    
    otio::ErrorStatus error_status;
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
        dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(input, &error_status)));
    if (!timeline || otio::is_error(error_status))
    {
        examples::print_error(error_status);
        exit(1);
    }
    const int count = conform_timeline(timeline, folder);
    std::cout << "Relinked " << count << " clips to new media." << std::endl;
    if (!timeline.value->to_json_file(output, &error_status))
    {
        examples::print_error(error_status);
        exit(1);
    }
    const auto clips = timeline->find_clips(&error_status);
    if (otio::is_error(error_status))
    {
        examples::print_error(error_status);
        exit(1);
    }
    std::cout << "Saved " << output << " with " << clips.size() << " clips." << std::endl;
    
    return 0;
}
