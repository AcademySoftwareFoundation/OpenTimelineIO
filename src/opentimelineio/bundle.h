// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Timeline;

/// @todo Should the .otioz/.otiod file versions be bumped?
/// @todo Shoudle we use a library for URL conversions?
/// @todo Add support for dry runs?
/// @todo Document that paths are relative to the timeline.
/// @todo Should bundle support be optional?
/// @todo Add C++ bundle tests.
/// @todo Python wrappings.
/// @todo Convert Python adapters to use C++ functions.
/// @todo Update documentation.
namespace bundle {

/// @brief This constant provides the current otioz version.
static std::string const otioz_version = "1.0.0";

/// @brief This constant provides the current otiod version.
static std::string const otiod_version = "1.0.0";

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
    MediaReferencePolicy media_reference_policy =
        MediaReferencePolicy::ErrorIfNotFile;
    int indent = 4;
};

/// @brief Write a timeline and it's referenced media to an .otioz bundle.
///
/// @param timeline The timeline to write.
/// @param timeline_dir The timeline's parent directory. This is used to locate
///        media with relative file paths.
/// @param file_name The bundle file name.
/// @param media_reference_policy The media reference policy.
/// @param error_status The error status.
/// @param target_family_label_spec @todo Add comment.
/// @param indent The number of spaces to use for indentation.
bool to_otioz(
    Timeline const*           timeline,
    std::string const&        timeline_dir,
    std::string const&        file_name,
    ToBundleOptions const&    options                  = ToBundleOptions(),
    ErrorStatus*              error_status             = nullptr,
    schema_version_map const* target_family_label_spec = nullptr);

/// @brief Read a timeline from an .otioz bundle. The timeline and timeline
/// file name are returned.
///
/// @param file_name The bundle file name.
/// @param output_dir The directory where the bundle will be extracted.
/// @param error_status The error status.
std::pair<SerializableObject::Retainer<Timeline>, std::string> from_otioz(
    std::string const& file_name,
    std::string const& output_dir,
    ErrorStatus*       error_status = nullptr);

/// @brief Write a timeline and it's referenced media to an .otiod bundle.
///
/// @param timeline The timeline to write.
/// @param timeline_dir The timeline's parent directory. This is used to locate
///        media with relative file paths.
/// @param file_name The bundle file name.
/// @param media_reference_policy The media reference policy.
/// @param error_status The error status.
/// @param target_family_label_spec @todo Add comment.
/// @param indent The number of spaces to use for indentation.
bool to_otiod(
    Timeline const*           timeline,
    std::string const&        timeline_dir,
    std::string const&        file_name,
    ToBundleOptions const&    options                  = ToBundleOptions(),
    ErrorStatus*              error_status             = nullptr,
    schema_version_map const* target_family_label_spec = nullptr);

/// @brief Options for reading .otiod bundles.
struct FromOtiodOptions
{
    bool absolute_media_reference_paths = false;
};

/// @brief Read a timeline from an .otiod bundle. The timeline and timeline
/// file name are returned.
///
/// @param file_name The bundle file name.
/// @param timeline_file_name Returns the timeline file name.
/// @param error_status The error status.
std::pair<SerializableObject::Retainer<Timeline>, std::string> from_otiod(
    std::string const&      file_name,
    FromOtiodOptions const& options      = FromOtiodOptions(),
    ErrorStatus*            error_status = nullptr);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
