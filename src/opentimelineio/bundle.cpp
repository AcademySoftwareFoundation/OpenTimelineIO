// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/bundleUtils.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

size_t
get_media_size(
    Timeline const*     timeline,
    WriteOptions const& options,
    ErrorStatus*        error_status)
{
    size_t byte_count = 0;
    try
    {
        // Get the file manifest.
        std::map<std::filesystem::path, std::filesystem::path> manifest;
        timeline_for_bundle_and_manifest(
            timeline,
            std::filesystem::u8path(options.parent_path),
            options.media_policy,
            manifest);

        // Count the bytes in each file.
        for (auto const& file: manifest)
        {
            byte_count += std::filesystem::file_size(file.first);
        }
    }
    catch (std::exception const& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::BUNDLE_SIZE_ERROR, e.what());
        }
    }
    return byte_count;
}

} // namespace bundle
}} // namespace bundle::opentimelineio::OPENTIMELINEIO_VERSION
