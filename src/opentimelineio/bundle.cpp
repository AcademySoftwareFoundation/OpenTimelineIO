// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/imageSequenceReference.h"
#include "opentimelineio/missingReference.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <sstream>

#if defined(OTIO_MINIZ_SRC)
// miniz is included directly into this translation unit, wrapped in an
// anonymous namespace, so that all of miniz's symbols are local to this
// .cpp file. This prevents link-time conflicts with other zip libraries
// (e.g. minizip-ng) that downstream OTIO consumers may already be linking.
// The Windows headers below must be pre-included at global scope because
// the Win32 Interlocked intrinsics are defined as inline functions in
// <winbase.h> and don't tolerate being placed inside a namespace.
#ifdef _WIN32
  #ifndef WIN32_LEAN_AND_MEAN
    #define WIN32_LEAN_AND_MEAN
  #endif
  #include <windows.h>
  #include <io.h>
  #include <sys/stat.h>
#endif
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
namespace {
    #ifdef __GNUC__
      #pragma GCC diagnostic push
      #pragma GCC diagnostic ignored "-Wunused-function"
    #endif
    #include "miniz.c"
    #ifdef __GNUC__
      #pragma GCC diagnostic pop
    #endif
}
#else // OTIO_MINIZ_SRC
#include <miniz.h>
#endif // OTIO_MINIZ_SRC

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {
namespace bundle {

    // File contents:
    // - URL parsing utilities (percent_decode, starts_with, to_lower, file_from_url)
    // - BundleFile and bundle file processing
    // - ZipWriter and ZipReader
    // - Public API (dry_run, write_otioz, read_otioz, write_otiod, read_otiod)

    namespace {

        // Utility to decode a URL (ie, %20 -> ' ')
        std::string percent_decode(std::string const& s)
        {
            std::string result;
            result.reserve(s.size());
            for (size_t i = 0; i < s.size(); ++i)
            {
                if (s[i] == '%' && i + 2 < s.size())
                {
                    int hi = std::stoi(s.substr(i + 1, 2), nullptr, 16);
                    result += static_cast<char>(hi);
                    i += 2;
                }
                else
                {
                    result += s[i];
                }
            }
            return result;
        }

        // Utility to check if a string has the given prefix, case insensitive
        bool starts_with(std::string_view s, std::string_view prefix)
        {
            if (s.size() < prefix.size()) return false;
            for (size_t i = 0; i < prefix.size(); ++i)
            {
                if (std::tolower(static_cast<unsigned char>(s[i])) != prefix[i]) return false;
            }
            return true;
        }
        
        // Utility to lowercase a string
        std::string to_lower(std::string const& s)
        {
            std::string out = s;
            std::transform(out.begin(), out.end(), out.begin(),
                [](unsigned char c){ return static_cast<char>(std::tolower(c)); });
            return out;
        }

        // This struct contains the source path and archive name for each
        // file to be added to the bundle
        struct BundleFile
        {
            std::string source_path;
            std::string archive_name;

            bool operator<(BundleFile const& other) const
            {
                return std::tie(source_path, archive_name) <
                       std::tie(other.source_path, other.archive_name);
            }
        };
        using BundleFiles = std::set<BundleFile>;

        // Check and add files to the bundle. This is a convenience function
        // used by process_media_references().
        bool register_bundle_file(
            std::filesystem::path const& source_path,
            std::filesystem::path const& relative_media_path,
            std::map<std::string, std::filesystem::path>& paths,
            BundleFiles& out,
            ErrorStatus* error_status)
        {
            // Check if this file would overwrite any others
            auto const paths_key = to_lower(source_path.filename().u8string());
            auto const i = paths.find(paths_key);
            if (i != paths.end() &&
                source_path.parent_path() != i->second.parent_path())
            {
                if (error_status) {
                    std::stringstream ss;
                    ss << "media file " << source_path
                        << " would overwrite " << i->second;
                    *error_status = ErrorStatus(
                        ErrorStatus::FILE_WRITE_FAILED, ss.str());
                }
                return false;
            }
            paths[paths_key] = source_path;
           
            // Add the file to the bundle list
            auto resolved = source_path;
            if (resolved.is_relative() && !relative_media_path.empty())
                resolved = relative_media_path / resolved;
            auto const bundle_path = (std::filesystem::u8path(media_dir) /
                source_path.filename()).u8string();
            out.insert({ resolved.u8string(), bundle_path });
            return true;
        }

        // Process all media references according to the policy. The list of
        // files to be added to the bundle is returned.
        bool process_media_references(
            Timeline*                    timeline,
            std::filesystem::path const& relative_media_path,
            MediaReferencePolicy         policy,
            ErrorStatus*                 error_status,
            BundleFiles&                 out)
        {
            // Store a map of the processed paths to check we are not
            // overwriting any media in the bundle
            std::map<std::string, std::filesystem::path> paths;
            
            // Iterate over all the clips
            for (auto clip : timeline->find_clips())
            {
                // Get the media reference retainers
                std::map<std::string, SerializableObject::Retainer<MediaReference>> refs;
                for (auto i : clip->media_references())
                {
                    refs[i.first] = i.second;
                }

                // Iterate over the media references
                bool modified = false;
                for (auto& ref : refs)
                {
                    std::optional<std::string> file;
                    if (auto ext = dynamic_retainer_cast<ExternalReference>(ref.second))
                    {
                        // Handle external references
                        file = file_from_url(ext->target_url());
                        if (file.has_value() &&
                            policy != MediaReferencePolicy::all_missing)
                        {
                            auto const path = std::filesystem::u8path(*file);
                            if (!register_bundle_file(
                                path,
                                relative_media_path,
                                paths,
                                out,
                                error_status))
                                return false;
                            
                            // Set the URL to the bundle location
                            ext->set_target_url((std::filesystem::u8path(media_dir) /
                                path.filename()).u8string());
                        }
                    }
                    else if (auto seq = dynamic_retainer_cast<ImageSequenceReference>(ref.second))
                    {
                        // Handle image sequence references
                        if (policy != MediaReferencePolicy::all_missing)
                        {
                            for (int frame = 0;
                                frame < seq->number_of_images_in_sequence();
                                frame += seq->frame_step())
                            {
                                file = file_from_url(seq->target_url_for_image_number(frame));
                                if (file.has_value())
                                {
                                    const auto path = std::filesystem::u8path(*file);
                                    if (!register_bundle_file(
                                        path,
                                        relative_media_path,
                                        paths,
                                        out,
                                        error_status))
                                        return false;
                                }
                            }
                            
                            // Set the URL to the bundle location
                            seq->set_target_url_base(std::string(media_dir) + "/");
                        }
                    }
                    
                    // Handle the policy for this reference
                    if (ref.second &&
                        !dynamic_retainer_cast<MissingReference>(ref.second))
                    {
                        switch (policy)
                        {
                        case MediaReferencePolicy::error_if_not_file:
                            if (!file.has_value())
                            {
                                if (error_status)
                                    *error_status = ErrorStatus(
                                        ErrorStatus::FILE_WRITE_FAILED,
                                        "media reference is not a file");
                                return false;
                            }
                            break;
                        case MediaReferencePolicy::missing_if_not_file:
                            if (!file.has_value())
                            {
                                // \todo Add missing reference metadata
                                ref.second = new MissingReference(ref.second->name());
                                modified = true;
                            }
                            break;
                        case MediaReferencePolicy::all_missing:
                            // \todo Add missing reference metadata
                            ref.second = new MissingReference(ref.second->name());
                            modified = true;
                            break;
                        default: break;
                        }
                    }
                }

                if (modified)
                {
                    // Set the new media references on the clip
                    Clip::MediaReferences ref_ptrs;
                    for (auto i : refs)
                    {
                        ref_ptrs[i.first] = i.second;
                    }
                    clip->set_media_references(
                        ref_ptrs,
                        clip->active_media_reference_key());
                }
            }
            return true;
        }
        
        // Common code for preparing the bundle
        bool prepare_bundle(
            Timeline const*                         timeline,
            WriteOptions const&                     options,
            ErrorStatus*                            error_status,
            SerializableObject::Retainer<Timeline>& out_clone,
            std::string&                            out_json,
            BundleFiles&                            out_files)
        {
            // Clone the timeline so we can make modifications
            out_clone = SerializableObject::Retainer<Timeline>(
                dynamic_cast<Timeline*>(timeline->clone(error_status)));
            if (!out_clone || is_error(error_status))
                return false;
           
            // Get the relative media path
            std::filesystem::path relative_media_path;
            if (options.relative_media_path.has_value())
                relative_media_path = std::filesystem::u8path(*options.relative_media_path);
           
            // Process the media references and get the list of files to add
            // to the bundle
            if (!process_media_references(
                out_clone,
                relative_media_path,
                options.policy,
                error_status,
                out_files))
                return false;
           
            // Convert the new timeline to json for writing
            out_json = out_clone->to_json_string(
                error_status,
                nullptr,
                options.indent);
            return !is_error(error_status);
        }

        // Change relative paths to absolute
        void rewrite_media_to_absolute(
            Timeline* timeline,
            std::filesystem::path const& bundle_root)
        {
            for (auto clip : timeline->find_clips())
            {
                for (auto ref : clip->media_references())
                {
                    if (auto ext = dynamic_cast<ExternalReference*>(ref.second))
                    {
                        auto const current = std::filesystem::u8path(ext->target_url());
                        if (current.is_relative())
                        {
                            ext->set_target_url(
                                (bundle_root / current).lexically_normal().u8string());
                        }
                    }
                    else if (auto seq = dynamic_cast<ImageSequenceReference*>(ref.second))
                    {
                        auto const base = std::filesystem::u8path(seq->target_url_base());
                        if (base.is_relative())
                        {
                            auto absolute = (bundle_root / base).lexically_normal().u8string();
                            if (!absolute.empty() && absolute.back() != '/')
                                absolute += '/';
                            seq->set_target_url_base(absolute);
                        }
                    }
                }
            }
        }

        // This class writes a ZIP file using miniz
        class ZipWriter
        {
        public:
            ZipWriter(std::string const& path) :
                _path(path)
            {
                if (!mz_zip_writer_init_file_v2(&_zip, path.c_str(), 0, MZ_ZIP_FLAG_WRITE_ZIP64))
                {
                    throw std::runtime_error("cannot initialize zip writer");
                }
            }

            ~ZipWriter()
            {
                mz_zip_writer_end(&_zip);
                if (!_finalized)
                {
                    // Try and remove the file if it was partially written
                    std::error_code ec;
                    std::filesystem::remove(_path, ec);
                }
            }
            
            ZipWriter(ZipWriter const&) = delete;
            ZipWriter& operator=(ZipWriter const&) = delete;
            
            void add_text(std::string const& name, std::string const& text)
            {
                if (!mz_zip_writer_add_mem(
                    &_zip,
                    name.c_str(),
                    text.c_str(),
                    text.size(),
                    MZ_DEFAULT_LEVEL | MZ_ZIP_FLAG_WRITE_ZIP64))
                {
                    throw std::runtime_error("cannot add " + name + " to zip");
                }
            }
            
            void add_file_uncompressed(std::string const& name, std::string const& path)
            {
                if (!mz_zip_writer_add_file(
                    &_zip,
                    name.c_str(),
                    path.c_str(),
                    nullptr,
                    0,
                    MZ_NO_COMPRESSION | MZ_ZIP_FLAG_WRITE_ZIP64))
                {
                    throw std::runtime_error("cannot add " + path + " to zip");
                }
            }

            void finalize()
            {
                if (!mz_zip_writer_finalize_archive(&_zip))
                {
                    throw std::runtime_error("cannot finalize zip writer");
                }
                _finalized = true;
            }

        private:
            std::string _path;
            mz_zip_archive _zip = {};
            bool _finalized = false;
        };
        
        // This class reads a ZIP file using miniz
        class ZipReader
        {
        public:
            ZipReader(std::string const& path)
            {
                if (!mz_zip_reader_init_file(&_zip, path.c_str(), 0))
                {
                    throw std::runtime_error("cannot open zip file");
                }
            }
            
            ~ZipReader()
            {
                mz_zip_reader_end(&_zip);
            }
            
            ZipReader(ZipReader const&) = delete;
            ZipReader& operator=(ZipReader const&) = delete;
            
            mz_uint num_files() const
            {
                return mz_zip_reader_get_num_files(const_cast<mz_zip_archive*>(&_zip));
            }
            
            std::optional<mz_uint> find(std::string const& name)
            {
                int idx = mz_zip_reader_locate_file(&_zip, name.c_str(), nullptr, 0);
                if (idx < 0) return std::nullopt;
                return static_cast<mz_uint>(idx);
            }

            mz_zip_archive_file_stat stat(mz_uint i)
            {
                mz_zip_archive_file_stat s;
                if (!mz_zip_reader_file_stat(&_zip, i, &s))
                {
                    throw std::runtime_error("cannot stat zip entry");
                }
                return s;
            }

            std::string read_to_string(mz_uint i)
            {
                mz_zip_archive_file_stat s;
                if (!mz_zip_reader_file_stat(&_zip, i, &s))
                {
                    throw std::runtime_error("cannot stat zip entry");
                }
                
                std::string out;
                out.resize(s.m_uncomp_size);
                if (!mz_zip_reader_extract_to_mem(
                    &_zip,
                    i,
                    out.data(),
                    out.size(),
                    0))
                {
                    throw std::runtime_error("cannot extract zip entry to memory");
                }
                return out;
            }
            
            bool is_directory(mz_uint i)
            {
                return mz_zip_reader_is_file_a_directory(&_zip, i);
            }
            
            void extract_to_file(mz_uint i, std::string const& path)
            {
                if (!mz_zip_reader_extract_to_file(&_zip, i, path.c_str(), 0))
                {
                    throw std::runtime_error("cannot extract zip entry");
                }
            }

        private:
            mz_zip_archive _zip = {};
        };
    
        // Validate that an extraction path is contained within the destination
        // directory. Protects against zip slip vulnerabilities where archive
        // entries contain ".." or absolute paths.
        bool is_path_safe(
            std::filesystem::path const& dest_dir,
            std::filesystem::path const& out_path)
        {
            auto const canonical_dest = std::filesystem::weakly_canonical(dest_dir);
            auto const canonical_out = std::filesystem::weakly_canonical(out_path);
            auto const rel = std::filesystem::relative(canonical_out, canonical_dest);
            if (rel.empty()) return false;
            auto const first = rel.begin()->u8string();
            return first != "..";
        }
    }

    std::optional<std::string> file_from_url(std::string const& url)
    {
        constexpr std::string_view file_prefix = "file://";
        if (!starts_with(url, file_prefix))
        {
            if (url.find("://") != std::string::npos) return std::nullopt;
            return url;  // bare path
        }

        // Split "file://" + authority + path
        std::string rest = std::string(url.substr(file_prefix.size()));
        auto const slash = rest.find('/');
        std::string netloc = (slash == std::string::npos) ? rest : rest.substr(0, slash);
        std::string path   = (slash == std::string::npos) ? "" : rest.substr(slash);

        // Strip query/fragment from path
        if (auto pos = path.find('?'); pos != std::string::npos) path.resize(pos);
        if (auto pos = path.find('#'); pos != std::string::npos) path.resize(pos);

        // Decode the path
        path = percent_decode(path);

        auto is_drive = [](std::string const& s) {
            return s.size() == 2 &&
                   std::isalpha(static_cast<unsigned char>(s[0])) &&
                   s[1] == ':';
        };

        std::string result;

        if (is_drive(netloc))
        {
            // file://X:/path → X:/path
            result = netloc + path;
        }
        else if (path.size() >= 3 && path[0] == '/' && is_drive(path.substr(1, 2)))
        {
            // file://host/X:/path → X:/path (strip leading '/' and host)
            result = path.substr(1);
        }
        else if (!netloc.empty() && to_lower(netloc) != "localhost")
        {
            // file://host/path → //host/path (UNC)
            result = "//" + netloc + path;
        }
        else
        {
            // file:///path or file://localhost/path → /path
            result = path;
        }

        // Normalize separators
        std::replace(result.begin(), result.end(), '\\', '/');
        return result;
    }

    std::optional<uint64_t> dry_run(
        Timeline const*     timeline,
        WriteOptions const& options,
        ErrorStatus*        error_status)
    {
        // Prepare the bundle
        SerializableObject::Retainer<Timeline> clone;
        std::string                            json;
        BundleFiles                            files;
        if (!prepare_bundle(
            timeline,
            options,
            error_status,
            clone,
            json,
            files))
            return std::nullopt;
        
        // Add the version file and timeline file sizes
        uint64_t total = 0;
        total += std::string_view(version).size();
        total += json.size();
        
        // Add the media file sizes
        try
        {
            for (auto const& f : files)
            {
                total += std::filesystem::file_size(
                    std::filesystem::u8path(f.source_path));
            }
        }
        catch (std::exception const& e)
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    e.what());
            return std::nullopt;
        }
        
        return total;
    }

    bool write_otioz(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options,
        ErrorStatus*        error_status)
    {
        // Validate the path
        if (std::filesystem::exists(std::filesystem::u8path(path)))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_WRITE_FAILED,
                    "output path already exists");
            return false;
        }

        // Prepare the bundle
        SerializableObject::Retainer<Timeline> clone;
        std::string                            json;
        BundleFiles                            files;
        if (!prepare_bundle(
            timeline,
            options,
            error_status,
            clone,
            json,
            files))
            return false;

        // Write the bundle
        try
        {
            ZipWriter zw(path);
            zw.add_text(version_file, version);
            zw.add_text(timeline_file, json);
            for (const auto& i : files)
            {
                zw.add_file_uncompressed(i.archive_name, i.source_path);
            }
            zw.finalize();
        }
        catch (const std::exception& e)
        {
            if (error_status)
            {
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_WRITE_FAILED,
                    e.what());
            }
            return false;
        }
        return true;
    }

    SerializableObject* read_otioz(
        std::string const& path,
        ReadOptions const& options,
        ErrorStatus*       error_status)
    {
        // Validate the paths
        auto const input_path = std::filesystem::u8path(path);
        if (!std::filesystem::is_regular_file(input_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "input path is not a file");
            return nullptr;
        }
        std::filesystem::path output_path;
        if (options.extract_path.has_value())
        {
            output_path = options.extract_path.value();
            if (std::filesystem::exists(output_path))
            {
                if (error_status)
                    *error_status = ErrorStatus(
                        ErrorStatus::FILE_WRITE_FAILED,
                        "output directory already exists");
                return nullptr;
            }
        }

        // Read the archive
        std::string json;
        try
        {
            ZipReader zr(path);

            // Read the timeline
            auto timeline_idx = zr.find(timeline_file);
            if (!timeline_idx)
                throw std::runtime_error("bundle is missing content.otio");
            json = zr.read_to_string(*timeline_idx);

            // Extract the archive
            if (options.extract_path.has_value())
            {
                std::filesystem::create_directories(output_path);
            
                mz_uint const n = zr.num_files();
                for (mz_uint i = 0; i < n; ++i)
                {
                    auto const stat = zr.stat(i);
                    auto const file_path = output_path / std::filesystem::u8path(stat.m_filename);
                    
                    // Guard against zip slip
                    if (!is_path_safe(output_path, file_path))
                    {
                        throw std::runtime_error(
                            std::string("unsafe path in archive: ") + stat.m_filename);
                    }
                    
                    if (zr.is_directory(i))
                    {
                        std::filesystem::create_directories(file_path);
                    }
                    else
                    {
                        std::filesystem::create_directories(file_path.parent_path());
                        zr.extract_to_file(i, file_path.u8string());
                    }
                }
            }
        }
        catch (const std::exception& e)
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    e.what());

            if (options.extract_path.has_value())
            {
                // Try and remove the directory if it was partially written
                std::error_code ec;
                std::filesystem::remove_all(output_path, ec);
            }

            return nullptr;
        }

        // Create the timeline
        auto result = Timeline::from_json_string(json, error_status);
        if (!result || is_error(error_status))
            return nullptr;

        // Optionally make the media reference paths absolute
        if (options.absolute_media_reference_paths &&
            options.extract_path)
        {
            if (auto timeline = dynamic_cast<Timeline*>(result))
            {
                rewrite_media_to_absolute(
                    timeline,
                    std::filesystem::u8path(options.extract_path.value()));
            }
        }

        return result;
    }

    bool write_otiod(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options,
        ErrorStatus*        error_status)
    {
        // Validate the path
        auto const output_path = std::filesystem::u8path(path);
        if (std::filesystem::exists(output_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_WRITE_FAILED,
                    "output path already exists");
            return false;
        }

        // Prepare the bundle
        SerializableObject::Retainer<Timeline> clone;
        std::string                            json;
        BundleFiles                            files;
        if (!prepare_bundle(
            timeline,
            options,
            error_status,
            clone,
            json,
            files))
            return false;

        // Write the bundle
        try
        {
            // Create the output directories
            std::filesystem::create_directories(output_path);
            std::filesystem::create_directory(output_path / media_dir);
            
            // Write the version file
            {
                std::ofstream of(output_path / version_file);
                of.exceptions(std::ios::failbit | std::ios::badbit);
                of << version;
            }
            
            // Write the timeline
            {
                std::ofstream of(output_path / timeline_file);
                of.exceptions(std::ios::failbit | std::ios::badbit);
                of << json;
            }
            
            // Copy the media files
            for (const auto& i : files)
            {
                std::filesystem::copy_file(
                    i.source_path,
                    output_path / std::filesystem::u8path(i.archive_name));
            }
        }
        catch (const std::exception& e)
        {
            if (error_status)
            {
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_WRITE_FAILED,
                    e.what());
            }
            return false;
        }
        return true;
    }

    SerializableObject* read_otiod(
        std::string const& path,
        ReadOptions const& options,
        ErrorStatus*       error_status)
    {
        // Validate the paths
        auto const input_path = std::filesystem::u8path(path);
        if (!std::filesystem::is_directory(input_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "input path is not a directory");
            return nullptr;
        }
        auto const version_path = input_path / version_file;
        auto const timeline_path = input_path / timeline_file;
        if (!std::filesystem::is_regular_file(version_path) ||
            !std::filesystem::is_regular_file(timeline_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "bundle is missing required files");
            return nullptr;
        }
        
        // Read the timeline
        auto result = Timeline::from_json_file(
            timeline_path.u8string(),
            error_status);
        if (!result || is_error(error_status))
            return nullptr;
        
        // Optionally make the media reference paths absolute
        if (options.absolute_media_reference_paths)
        {
            if (auto timeline = dynamic_cast<Timeline*>(result))
            {
                rewrite_media_to_absolute(
                    timeline,
                    timeline_path.parent_path());
            }
        }

        return result;
    }
}
}
}

