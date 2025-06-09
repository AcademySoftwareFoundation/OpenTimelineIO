// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @todo Should the .otioz/.otiod file versions be bumped?
/// @todo Shoudle we use a library for URL conversions?
/// @todo Document that paths are relative to the timeline.
/// @todo Should bundle support be optional?
/// @todo Add C++ image sequence bundle tests.
/// @todo Python wrappings.
/// @todo Convert Python adapters to use C++ functions.
/// @todo Update documentation.
namespace bundle {

/// @brief The current otioz version.
static std::string const otioz_version = "1.0.0";

/// @brief The current otiod version.
static std::string const otiod_version = "1.0.0";

/// @brief The version file name in the bundle.
static std::string const version_file = "version.txt";

/// @brief The OTIO file name in the bundle.
static std::string const otio_file = "content.otio";

/// @brief The media directory name in the bundle.
static std::string const media_dir = "media";

/// @brief This enumeration provides the bundle media reference policy.
enum class MediaReferencePolicy
{
    ErrorIfNotFile,   ///< Return an error if there are any non-file media references.
    MissingIfNotFile, ///< Replace non-file media references with missing references.
    AllMissing        ///< Replace all media references with missing references.
};

/// @brief Options for writing bundles.
struct ToBundleOptions
{
    /// @brief The parent path is used to locate media with relative paths. If
    /// parent path is empty, paths are relative to the current working directory.
    std::string parent_path;

    /// @brief The bundle media reference policy.
    MediaReferencePolicy media_reference_policy =
        MediaReferencePolicy::ErrorIfNotFile;

    /// @todo Add comment.
    schema_version_map const* target_family_label_spec = nullptr;

    /// @brief The number of spaces to use for JSON indentation.
    int indent = 4;
};

/// @brief Get the total size (in bytes) of the media files that will be
/// put into the bundle.
size_t get_media_size(
    Timeline const*        timeline,
    ToBundleOptions const& options      = ToBundleOptions(),
    ErrorStatus*           error_status = nullptr);

/// @brief Write a timeline and it's referenced media to an .otioz bundle.
///
/// Takes as input an OTIO file that has media references which are all
/// ExternalReferences with target_urls to files with unique basenames that are
/// accessible through the file system and bundles those files and the otio
/// file into a single zip file with the suffix .otioz.
///
/// The otio file and version file are compressed using the ZIP "deflate"
/// mode. All media files are store uncompressed.
///
/// Can error out if files are not locally referenced. or provide missing
/// references.
///
/// Note that OTIOZ files _always_ use the unix style path separator ('/').
/// This ensures that regardless of which platform a bundle was created on, it
/// can be read on UNIX and Windows platforms.
///
/// @param timeline The timeline to write.
/// @param file_name The bundle file name.
/// @param options The bundle options.
/// @param error_status The error status.
bool to_otioz(
    Timeline const*        timeline,
    std::string const&     file_name,
    ToBundleOptions const& options      = ToBundleOptions(),
    ErrorStatus*           error_status = nullptr);

/// @brief Options for reading .otioz bundles.
struct FromOtiozOptions
{
    /// @brief Extract the contents of the bundle to the given path. If the
    /// path is empty, the contents are not extracted, and only the timeline
    /// is read from the bundle.
    std::string extract_path;
};

/// @brief Read a timeline from an .otioz bundle.
///
/// @param file_name The bundle file name.
/// @param output_dir The directory where the bundle will be extracted.
/// @param error_status The error status.
Timeline* from_otioz(
    std::string const&      file_name,
    FromOtiozOptions const& options      = FromOtiozOptions(),
    ErrorStatus*            error_status = nullptr);

/// @brief Write a timeline and it's referenced media to an .otiod bundle.
///
/// Takes as input an OTIO file that has media references which are all
/// ExternalReferences with target_urls to files with unique basenames that are
/// accessible through the file system and bundles those files and the otio file
/// into a single directory named with a suffix of .otiod.
///
/// @param timeline The timeline to write.
/// @param file_name The bundle file name.
/// @param options The bundle options.
/// @param error_status The error status.
bool to_otiod(
    Timeline const*        timeline,
    std::string const&     file_name,
    ToBundleOptions const& options      = ToBundleOptions(),
    ErrorStatus*           error_status = nullptr);

/// @brief Options for reading .otiod bundles.
struct FromOtiodOptions
{
    /// @brief Use absolute paths for media references.
    bool absolute_media_reference_paths = false;
};

/// @brief Read a timeline from an .otiod bundle.
///
/// @param file_name The bundle file name.
/// @param timeline_file_name Returns the timeline file name.
/// @param error_status The error status.
Timeline* from_otiod(
    std::string const&      file_name,
    FromOtiodOptions const& options      = FromOtiodOptions(),
    ErrorStatus*            error_status = nullptr);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
