// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/typeRegistry.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Timeline;

/// @todo Should the file versions be bumped?
/// @todo Add support for dry runs?
/// @todo Document that relative paths are relative to the timeline.
namespace bundle {

/// @brief This constant provides the current otioz version.
static std::string const otiozVersion = "1.0.0";

/// @brief This constant provides the current otiod version.
static std::string const otiodVersion = "1.0.0";

/// @brief This enumeration provides the bundle media reference policy.
enum class MediaReferencePolicy
{
    ErrorIfNotFile,
    MissingIfNotFile,
    AllMissing
};

/// @brief Write a timeline and it's referenced media to an .otiod bundle.
///
/// @param timeline The timeline to write.
/// @param timeline_dir The timeline's parent directory.
/// @param file_name The bundle file name.
/// @param media_reference_policy The media reference policy.
/// @param error_status The return status.
/// @param target_family_label_spec @todo Add comment.
/// @param indent The number of spaces to use for indentation.
bool to_otiod(
    Timeline const*      timeline,
    std::string const&   timeline_dir,
    std::string const&   file_name,
    MediaReferencePolicy media_reference_policy =
        MediaReferencePolicy::ErrorIfNotFile,
    ErrorStatus*              error_status             = nullptr,
    const schema_version_map* target_family_label_spec = nullptr,
    int                       indent                   = 4);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
