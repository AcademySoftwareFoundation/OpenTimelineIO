// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Timeline;

/// @todo Should the .otioz/.otiod file versions be bumped?
/// @todo Shoudle we use a library for URL conversions?
/// @todo Document that paths are relative to the timeline.
/// @todo Should bundle support be optional?
/// @todo Add C++ image sequence bundle tests.
/// @todo Python wrappings.
/// @todo Convert Python adapters to use C++ functions.
/// @todo Update documentation.
namespace bundle {

/// @brief This constant provides the current otioz version.
static std::string const otioz_version = "1.0.0";

/// @brief This constant provides the current otiod version.
static std::string const otiod_version = "1.0.0";

/// @brief Version file name.
static std::string const version_file = "version.txt";

/// @brief OTIO file name.
static std::string const otio_file = "content.otio";

/// @brief Media directory name.
static std::string const media_dir = "media";

/// @brief This enumeration provides the bundle media reference policy.
enum class MediaReferencePolicy
{
    ErrorIfNotFile,
    MissingIfNotFile,
    AllMissing
};

/// @brief Options for writing bundles.
struct ToBundleOptions
{
    /// @brief The timeline's parent directory. This is used to locate media
    /// with relative file paths.
    std::string timeline_dir;

    /// @brief The media reference policy.
    MediaReferencePolicy media_reference_policy =
        MediaReferencePolicy::ErrorIfNotFile;

    /// @todo Add comment.
    schema_version_map const* target_family_label_spec = nullptr;

    /// @brief The number of spaces to use for indentation.
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
    /// @brief Extract the contents of the bundle.
    bool extract = false;

    /// @brief The output directory for the extracted contents.
    std::string output_dir;
};

/// @brief Read a timeline from an .otioz bundle.
///
/// @param file_name The bundle file name.
/// @param output_dir The directory where the bundle will be extracted.
/// @param error_status The error status.
SerializableObject::Retainer<Timeline> from_otioz(
    std::string const&      file_name,
    FromOtiozOptions const& options      = FromOtiozOptions(),
    ErrorStatus*            error_status = nullptr);

/// @brief Write a timeline and it's referenced media to an .otiod bundle.
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
SerializableObject::Retainer<Timeline> from_otiod(
    std::string const&      file_name,
    FromOtiodOptions const& options      = FromOtiodOptions(),
    ErrorStatus*            error_status = nullptr);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
