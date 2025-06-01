// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/timeline.h"

#include <filesystem>
#include <fstream>
#include <sstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace bundle {

bool
to_otiod(
    Timeline const*           timeline,
    std::string const&        timeline_dir,
    std::string const&        file_name,
    MediaReferencePolicy      media_reference_policy,
    ErrorStatus*              error_status,
    schema_version_map const* target_family_label_spec,
    int                       indent)
{
    try
    {
        // Check that the path does not exist.
        std::filesystem::path const path = std::filesystem::u8path(file_name);
        if (std::filesystem::exists(path))
        {
            std::stringstream ss;
            ss << "'" << path.u8string() << "' exists, will not overwrite.";
            throw std::runtime_error(ss.str());
        }

        // Check that the parent path exists.
        std::filesystem::path const parent_path = path.parent_path();
        if (!std::filesystem::exists(parent_path))
        {
            std::stringstream ss;
            ss << "Directory '" << parent_path.u8string()
               << "' does not exist, cannot create '" << path.u8string()
               << "'.";
            throw std::runtime_error(ss.str());
        }

        // Check that the parent path is a directory.
        if (!std::filesystem::is_directory(parent_path))
        {
            std::stringstream ss;
            ss << "'" << parent_path.u8string()
               << "' is not a directory, cannot create '" << path.u8string()
               << "'.";
            throw std::runtime_error(ss.str());
        }

        // General algorithm for the file bundles:
        //
        // * Build the file manifest (list of paths to files on disk that will be
        //   put into the archive).
        // * Build a mapping of path to file on disk to url to put into the media
        //   reference in the result.
        // * Relink the media references to point at the final location inside the
        //   archive.
        // * Build the resulting structure (zip file, directory).
        std::map<
            std::string,
            std::vector<SerializableObject::Retainer<ExternalReference>>>
             path_to_mr_map;
        auto result_timeline = timeline_for_bundle_and_manifest(
            timeline,
            timeline_dir,
            media_reference_policy,
            path_to_mr_map);

        // Relink all the media references to their target paths.
        std::map<std::filesystem::path, std::filesystem::path>
            abspath_to_output_path_map;
        for (auto const& i: path_to_mr_map)
        {
            std::filesystem::path const target =
                path / std::filesystem::u8path(media_dir)
                / std::filesystem::u8path(i.first).filename();

            // Conform to POSIX style paths inside the bundle, so that they are
            // portable between windows and UNIX style environments.
            std::filesystem::path const final_path =
                std::filesystem::u8path(to_unix_separators(target.u8string()));

            // Cache the output path.
            abspath_to_output_path_map[i.first] = final_path;

            for (auto const& mr: i.second)
            {
                // Convert the relative path to a URL and set the media reference.
                std::string const url = url_from_filepath(
                    std::filesystem::relative(final_path, path).u8string());
                mr->set_target_url(url);
            }
        }

        // Create the output directory.
        std::filesystem::create_directory(path);

        // Write the version file.
        {
            std::ofstream               of;
            std::filesystem::path const version_path =
                path / std::filesystem::u8path(version_file);
            of.open(version_path);
            of << otiod_version << '\n';
        }

        // Write the .otio file.
        std::string const result_otio_file =
            (path / std::filesystem::u8path(otio_file)).u8string();
        if (!result_timeline->to_json_file(
                result_otio_file,
                error_status,
                target_family_label_spec,
                indent))
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

        // Create the media directory and copy the media files.
        //
        // @todo Can we use std::async to speed up file copies?
        std::filesystem::path const media_path =
            path / std::filesystem::u8path(media_dir);
        std::filesystem::create_directory(media_path);
        for (auto const& i: abspath_to_output_path_map)
        {
            std::filesystem::copy_file(i.first, i.second);
        }
    }
    catch (const std::exception& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, e.what());
        }
        return false;
    }
    return true;
}

std::pair<SerializableObject::Retainer<Timeline>, std::string>
from_otiod(
    std::string const& file_name,
    ErrorStatus* error_status)
{
    std::string const timeline_file_name =
        (std::filesystem::u8path(file_name)
         / std::filesystem::u8path(otio_file))
            .u8string();
    return std::make_pair(
        dynamic_cast<Timeline*>(
            Timeline::from_json_file(timeline_file_name, error_status)),
        timeline_file_name);
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
