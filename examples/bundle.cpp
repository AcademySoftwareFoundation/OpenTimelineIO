// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

// Example OTIO script that can create and extract bundles.

#include "util.h"

#include "opentimelineio/bundle.h"
#include "opentimelineio/fileUtils.h"
#include "opentimelineio/timeline.h"

#include <filesystem>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
namespace bundle = opentimelineio::OPENTIMELINEIO_VERSION::bundle;

bool
ends_with(std::string const& s, std::string const& find)
{
    size_t const s_size = s.size();
    size_t const find_size = find.size();
    return find_size < s_size ?
        s.substr(s_size - find_size, find_size) == find :
        false;
}

int
main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "Usage:\n";
        std::cout << "  bundle (input.otio) (output.otioz) - "
                  << "Create an .otioz bundle from an .otio file.\n";
        std::cout << "  bundle (input.otio) (output.otiod) - "
                  << "Create an .otiod bundle from an .otio file.\n";
        std::cout << "  bundle (input.otioz) (output) - "
                  << "Extract an .otioz bundle.\n";
        return 1;
    }
    const std::string input = otio::to_unix_separators(argv[1]);
    const std::string output = otio::to_unix_separators(argv[2]);

    if (ends_with(input, ".otio") && ends_with(output, ".otioz"))
    {
        // Open timeline.
        otio::ErrorStatus                                  error_status;
        otio::SerializableObject::Retainer<otio::Timeline> timeline(
            dynamic_cast<otio::Timeline*>(
                otio::Timeline::from_json_file(input, &error_status)));
        if (!timeline || otio::is_error(error_status))
        {
            examples::print_error(error_status);
            return 1;
        }

        // Create .otioz bundle.
        bundle::WriteOptions options;
        options.parent_path =
            std::filesystem::u8path(input).parent_path().u8string();
        if (!bundle::to_otioz(
            timeline.value,
            output,
            options,
            &error_status))
        {
            examples::print_error(error_status);
            return 1;
        }
    }
    else if (ends_with(input, ".otioz"))
    {
        // Extract .otioz bundle.
        bundle::OtiozReadOptions options;
        options.extract_path = output;
        otio::ErrorStatus error_status;
        auto result = bundle::from_otioz(input, options, &error_status);
        if (otio::is_error(error_status))
        {
            examples::print_error(error_status);
            return 1;
        }
    }
    else if (ends_with(input, ".otio") && ends_with(output, ".otiod"))
    {
        // Open timeline.
        otio::ErrorStatus                                  error_status;
        otio::SerializableObject::Retainer<otio::Timeline> timeline(
            dynamic_cast<otio::Timeline*>(
                otio::Timeline::from_json_file(input, &error_status)));
        if (!timeline || otio::is_error(error_status))
        {
            examples::print_error(error_status);
            return 1;
        }

        // Create .otiod bundle.
        bundle::WriteOptions options;
        options.parent_path =
            std::filesystem::u8path(input).parent_path().u8string();
        if (!bundle::to_otiod(
            timeline.value,
            output,
            options,
            &error_status))
        {
            examples::print_error(error_status);
            return 1;
        }
    }
    
    return 0;
}
