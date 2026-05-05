// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Utilities for working with OTIO bundles (.otioz and .otiod)
///
/// @todo Add .otioz description
/// @todo Add .otiod description
namespace bundle {

    /// @brief This constant provides the bundle file version.
    static char constexpr version[] = "1.0.0";

    /// @brief This constant provides the name of the bundled version file.
    static char constexpr version_file[] = "version.txt";

    /// @brief This constant provides the name of the bundled timeline file.
    static char constexpr timeline_file[] = "content.otio";

    /// @brief This constant provides the name of the bundled media sub-directory.
    static char constexpr media_dir[] = "media";

    /// @brief This enumeration provides the media reference policy.
    enum MediaReferencePolicy
    {
        error_if_not_file,
        missing_if_not_file,
        all_missing
    };

    /// @brief This struct provides options for writing bundles.
    struct OTIO_API_TYPE WriteOptions
    {
        /// @brief Base directory for resolving relative media reference paths.
        /// If a media reference URL resolves to a relative path, it is resolved
        /// against this directory before being added to the bundle.
        std::optional<std::string> relative_media_path;
        
        MediaReferencePolicy policy = MediaReferencePolicy::error_if_not_file;
    };

    /// @brief Write a timeline to an .otioz bundle.
    OTIO_API bool write_otioz(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options      = WriteOptions(),
        ErrorStatus*        error_status = nullptr);

    /// @brief Read an .otioz bundle.
    ///
    /// The archive contents are extracted into output_dir, which must not
    /// already exist.
    OTIO_API SerializableObject* read_otioz(
        std::string const& path,
        std::string const& output_dir,
        ErrorStatus*       error_status = nullptr);

    /// @brief Write a timeline to an .otiod bundle.
    OTIO_API bool write_otiod(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options      = WriteOptions(),
        ErrorStatus*        error_status = nullptr);

    /// @brief Read an .otiod bundle.
    OTIO_API SerializableObject* read_otiod(
        std::string const& path,
        ErrorStatus*       error_status = nullptr);
}
}
}

