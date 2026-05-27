// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Utilities for working with OTIO bundles (otioz and otiod)
///
/// https://opentimelineio.readthedocs.io/en/stable/tutorials/otio-filebundles.html#otioz-d-file-bundle-format-details
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
    ///
    /// Note that the policy is not applied to missing references. For
    /// example, if you have a timeline with missing references, those do not
    /// count as errors when the policy is set to error_if_not_file.
    enum MediaReferencePolicy
    {
        error_if_not_file,
        missing_if_not_file,
        all_missing
    };

    /// @brief Get a file from a URL.
    std::optional<std::string> file_from_url(std::string const& url);

    /// @brief Options for writing bundles.
    struct OTIO_API_TYPE WriteOptions
    {
        /// @brief Base directory for resolving relative media reference paths.
        /// If a media reference URL resolves to a relative path, it is resolved
        /// against this directory before being added to the bundle.
        std::optional<std::string> relative_media_path;
        
        /// @brief Media reference policy.
        MediaReferencePolicy policy = MediaReferencePolicy::error_if_not_file;
        
        /// @brief Number of spaces for JSON indentation.
        int indent = 4;
    };

    /// @brief Options for reading bundles.
    struct OTIO_API_TYPE ReadOptions
    {
        /// @brief Extract the contents of the otioz bundle to this directory,
        /// which must not already exist.
        std::optional<std::string> extract_path;
        
        /// @brief Convert the media reference paths to absolute paths.
        ///
        /// If this is set to true for otioz files, an extract_path must also be set.
        bool absolute_media_reference_paths = false;
    };

    /// @brief Check the timeline against the error policy to see if a bundle 
    /// can be made correctly.  If so, return the total uncompressed size of 
    /// the files that would be written to a bundle, without actually writing it. 
    /// This is useful for estimating the disk space required.
    OTIO_API std::optional<uint64_t> dry_run(
        Timeline const*     timeline,
        WriteOptions const& options      = WriteOptions(),
        ErrorStatus*        error_status = nullptr);

    /// @brief Write a timeline and it's referenced media to an otioz bundle.
    OTIO_API bool write_otioz(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options      = WriteOptions(),
        ErrorStatus*        error_status = nullptr);

    /// @brief Read a timeline from an otioz bundle.
    OTIO_API SerializableObject* read_otioz(
        std::string const& path,
        ReadOptions const& options      = ReadOptions(),
        ErrorStatus*       error_status = nullptr);

    /// @brief Write a timeline and it's referenced media to an otiod bundle.
    OTIO_API bool write_otiod(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options      = WriteOptions(),
        ErrorStatus*        error_status = nullptr);

    /// @brief Read a timeline from an otiod bundle.
    OTIO_API SerializableObject* read_otiod(
        std::string const& path,
        ReadOptions const& options      = ReadOptions(),
        ErrorStatus*       error_status = nullptr);
}
}
}

