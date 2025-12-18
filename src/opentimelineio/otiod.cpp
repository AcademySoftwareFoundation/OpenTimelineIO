// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/urlUtils.h"

#include <fstream>
#include <sstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

bool
to_otiod(
    Timeline const*     timeline,
    std::string const&  file_name,
    WriteOptions const& options,
    ErrorStatus*        error_status)
{
    try
    {
        // Check the path does not already exist.
        std::filesystem::path const path = std::filesystem::u8path(file_name);
        if (std::filesystem::exists(path))
        {
            std::stringstream ss;
            ss << "'" << path.u8string() << "' exists, will not overwrite.";
            throw std::runtime_error(ss.str());
        }

        // Check the parent path exists.
        std::filesystem::path const parent_path = path.parent_path();
        if (!std::filesystem::exists(parent_path))
        {
            std::stringstream ss;
            ss << "Directory '" << parent_path.u8string()
               << "' does not exist, cannot create '" << path.u8string()
               << "'.";
            throw std::runtime_error(ss.str());
        }

        // Check the parent path is a directory.
        if (!std::filesystem::is_directory(parent_path))
        {
            std::stringstream ss;
            ss << "'" << parent_path.u8string()
               << "' is not a directory, cannot create '" << path.u8string()
               << "'.";
            throw std::runtime_error(ss.str());
        }

        // Create the new timeline and file manifest.
        Manifest manifest;
        auto result_timeline = timeline_for_bundle_and_manifest(
            timeline,
            std::filesystem::u8path(options.parent_path),
            options.media_policy,
            manifest);

        // Create the output directory.
        std::filesystem::create_directory(path);

        // Write the version file.
        {
            std::ofstream of;
            of.open(path / version_file);
            of << otiod_version << '\n';
        }

        // Write the .otio file.
        std::string const result_otio_file = (path / otio_file).u8string();
        if (!result_timeline->to_json_file(
            result_otio_file,
            error_status,
            options.target_family_label_spec,
            options.indent))
        {
            std::stringstream ss;
            if (error_status)
            {
                ss << error_status->details;
            }
            else
            {
                ss << "Cannot write timeline: '" << result_otio_file << "'.";
            }
            throw std::runtime_error(ss.str());
        }

        // Create the media directory and copy the files from the manifest.
        //
        // @todo Can we use std::async to speed up file copies?
        std::filesystem::create_directory(path / media_dir);
        for (auto const& i: manifest)
        {
            std::filesystem::copy_file(i.first, path / i.second);
        }
    }
    catch (const std::exception& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::BUNDLE_WRITE_ERROR, e.what());
        }
        return false;
    }
    return true;
}

Timeline*
from_otiod(
    std::string const&      file_name,
    OtiodReadOptions const& options,
    ErrorStatus*            error_status)
{
    Timeline* timeline = nullptr;
    try
    {
        // Read the timeline.
        std::filesystem::path const timeline_path =
            std::filesystem::u8path(file_name) / otio_file;
        timeline = dynamic_cast<Timeline*>(
            Timeline::from_json_file(timeline_path.u8string(), error_status));

        if (options.absolute_media_reference_paths)
        {
            for (auto cl : timeline->find_clips())
            {
                if (auto er = dynamic_cast<ExternalReference*>(cl->media_reference()))
                {
                    std::filesystem::path const path =
                        timeline_path.parent_path()
                        / std::filesystem::u8path(
                            filepath_from_url(er->target_url()));
                    er->set_target_url(url_from_filepath(path.u8string()));
                }
            }
        }
    }
    catch (const std::exception& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::BUNDLE_READ_ERROR, e.what());
        }
    }
    return timeline;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
