// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/bundle.h"

#include <filesystem>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

/// @brief Convert a media reference policy to a string.
OTIO_API std::string to_string(MediaReferencePolicy);

/// @brief This maps absolute paths of media references to their relative
/// paths in the bundle media directory.
typedef std::map<std::filesystem::path, std::filesystem::path> Manifest;

/// @brief Create a new timeline based on the input timeline that has media
/// references replaced according to the media reference policy.
///
/// The media references are relinked to relative file paths in the media
/// directory.
///
/// This is considered an internal API.
/// 
/// Throws std::exception on errors.
OTIO_API SerializableObject::Retainer<Timeline> timeline_for_bundle_and_manifest(
    SerializableObject::Retainer<Timeline> const&,
    std::filesystem::path const& timeline_dir,
    MediaReferencePolicy media_reference_policy,
    Manifest& output_manifest);

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
