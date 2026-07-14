// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/imageSequenceReference.h"
#include "opentimelineio/missingReference.h"

#include <mz.h>
#include <mz_os.h>
#include <mz_strm.h>
#include <mz_zip.h>
#include <mz_zip_rw.h>

#include <algorithm>
#include <filesystem>
#include <fstream>

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
            std::filesystem::path const& relative_media_base_dir,
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
                if (error_status)
                    *error_status = ErrorStatus(
                        ErrorStatus::FILE_WRITE_FAILED,
                        "media file '" + source_path.u8string() +
                        "' would overwrite '" + i->second.u8string() + "'");
                return false;
            }
            paths[paths_key] = source_path;
           
            // Add the file to the bundle list
            auto resolved = source_path;
            if (resolved.is_relative() && !relative_media_base_dir.empty())
                resolved = relative_media_base_dir / resolved;
            auto const bundle_path = (std::filesystem::u8path(media_dir) /
                source_path.filename()).u8string();
            out.insert({ resolved.u8string(), bundle_path });
            return true;
        }

        // Utility to create a missing reference
        MissingReference* create_missing_reference(
            MediaReference* ref,
            std::string const& reason,
            std::optional<std::string> const& original_target_url)
        {
            auto out = new MissingReference(
                ref->name(),
                std::nullopt,
                ref->metadata());
            out->metadata()["missing_reference_because"] = reason;
            if (original_target_url.has_value())
            {
                out->metadata()["original_target_url"] = *original_target_url;
            }
            return out;
        }

        // Process all media references according to the policy. The list of
        // files to be added to the bundle is returned.
        bool process_media_references(
            Timeline*                    timeline,
            std::filesystem::path const& relative_media_base_dir,
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
                    std::optional<std::string> original_target_url;
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
                                relative_media_base_dir,
                                paths,
                                out,
                                error_status))
                                return false;
                            
                            // Set the URL to the bundle location
                            ext->set_target_url((std::filesystem::u8path(media_dir) /
                                path.filename()).u8string());
                        }

                        // Save the URL for the missing reference metadata
                        original_target_url = ext->target_url();
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
                                        relative_media_base_dir,
                                        paths,
                                        out,
                                        error_status))
                                        return false;
                                }
                            }
                            
                            // Set the URL to the bundle location
                            seq->set_target_url_base(std::string(media_dir) + "/");
                        }

                        // Save the URL for the missing reference metadata
                        original_target_url = file_from_url(seq->target_url_for_image_number(0));
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
                                        "media reference '" +
                                        ref.second->name() + "' is not a file");
                                return false;
                            }
                            break;
                        case MediaReferencePolicy::missing_if_not_file:
                            if (!file.has_value())
                            {
                                ref.second = create_missing_reference(
                                    ref.second,
                                    "'missing_if_not_file' specified as the MediaReferencePolicy",
                                    original_target_url);
                                modified = true;
                            }
                            break;
                        case MediaReferencePolicy::all_missing:
                        {
                            ref.second = create_missing_reference(
                                ref.second,
                                "'all_missing' specified as the MediaReferencePolicy",
                                original_target_url);
                            modified = true;
                            break;
                        }
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
            std::filesystem::path relative_media_base_dir;
            if (options.relative_media_base_dir.has_value())
                relative_media_base_dir = std::filesystem::u8path(
                    *options.relative_media_base_dir);
           
            // Process the media references and get the list of files to add
            // to the bundle
            if (!process_media_references(
                out_clone,
                relative_media_base_dir,
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

        // This class writes a ZIP file using minizip-ng
        class ZipWriter
        {
        public:
            ZipWriter(std::string const& path) :
                _path(path)
            {
                _writer = mz_zip_writer_create();
                if (!_writer)
                    throw std::runtime_error(
                        "cannot create zip writer for '" + path + "'");
                if (mz_zip_writer_open_file(_writer, path.c_str(), 0, 0) != MZ_OK)
                {
                    mz_zip_writer_delete(&_writer);
                    throw std::runtime_error(
                        "cannot initialize zip writer for '" + path + "'");
                }
            }

            ~ZipWriter()
            {
                if (_writer)
                {
                    if (!_finalized)
                        mz_zip_writer_close(_writer);
                    mz_zip_writer_delete(&_writer);
                }
                if (!_finalized)
                {
                    std::error_code ec;
                    std::filesystem::remove(_path, ec);
                }
            }

            ZipWriter(ZipWriter const&) = delete;
            ZipWriter& operator=(ZipWriter const&) = delete;

            void add_text(std::string const& name, std::string const& text)
            {
                if (text.size() > static_cast<size_t>(INT32_MAX))
                    throw std::runtime_error(
                        "text entry '" + name + "' too large for zip '" +
                        _path + "'");

                mz_zip_file file_info = {};
                file_info.filename = name.c_str();
                file_info.modified_date = time(nullptr);
                file_info.version_madeby = MZ_VERSION_MADEBY;
                file_info.compression_method = MZ_COMPRESS_METHOD_DEFLATE;
                file_info.flag = MZ_ZIP_FLAG_UTF8;

                if (mz_zip_writer_add_buffer(
                        _writer,
                        const_cast<char*>(text.data()),
                        static_cast<int32_t>(text.size()),
                        &file_info) != MZ_OK)
                {
                    throw std::runtime_error(
                        "cannot add '" + name + "' to zip '" + _path + "'");
                }
            }

            void add_file_uncompressed(std::string const& name, std::string const& path)
            {
                mz_zip_writer_set_compress_method(_writer, MZ_COMPRESS_METHOD_STORE);
                int32_t const err = mz_zip_writer_add_file(_writer, path.c_str(), name.c_str());
                mz_zip_writer_set_compress_method(_writer, MZ_COMPRESS_METHOD_DEFLATE);
                if (err != MZ_OK)
                    throw std::runtime_error(
                        "cannot add '" + path + "' to zip '" + _path + "'");
            }

            void finalize()
            {
                if (_finalized) return;
                if (mz_zip_writer_close(_writer) != MZ_OK)
                    throw std::runtime_error(
                        "cannot finalize zip writer for '" + _path + "'");
                _finalized = true;
            }

        private:
            std::string _path;
            void* _writer = nullptr;
            bool _finalized = false;
        };
        
        // This class reads a ZIP file using minizip-ng
        class ZipReader
        {
        public:
            ZipReader(std::string const& path)
            {
                _path = path;
                _reader = mz_zip_reader_create();
                if (!_reader)
                    throw std::runtime_error(
                        "cannot create zip reader for '" + path + "'");
                if (mz_zip_reader_open_file(_reader, path.c_str()) != MZ_OK)
                {
                    mz_zip_reader_delete(&_reader);
                    throw std::runtime_error(
                        "cannot open zip file '" + path + "'");
                }
            }

            ~ZipReader()
            {
                if (_reader)
                    mz_zip_reader_delete(&_reader);
            }

            ZipReader(ZipReader const&) = delete;
            ZipReader& operator=(ZipReader const&) = delete;

            // Read a named entry to a string (used for content.otio). Returns nullopt
            // if the entry is not present.
            std::optional<std::string> read_to_string(std::string const& name)
            {
                if (mz_zip_reader_locate_entry(_reader, name.c_str(), 0) != MZ_OK)
                    return std::nullopt;
                if (mz_zip_reader_entry_open(_reader) != MZ_OK)
                    throw std::runtime_error(
                        "cannot open zip entry '" + name + "' in '" +
                        _path + "'");

                // Close the entry on any exit path.
                struct EntryScope {
                    void* r; ~EntryScope() { mz_zip_reader_entry_close(r); }
                } scope{ _reader };

                mz_zip_file* info = nullptr;
                if (mz_zip_reader_entry_get_info(_reader, &info) != MZ_OK || !info)
                    throw std::runtime_error(
                        "cannot stat zip entry '" + name + "' in '" +
                        _path + "'");
                if (info->uncompressed_size < 0 ||
                    info->uncompressed_size > static_cast<int64_t>(INT32_MAX))
                    throw std::runtime_error(
                        "zip entry '" + name + "' too large in '" +
                        _path + "'");

                std::string out(static_cast<size_t>(info->uncompressed_size), '\0');
                int32_t const n = mz_zip_reader_entry_read(
                    _reader, out.data(), static_cast<int32_t>(out.size()));
                if (n != static_cast<int32_t>(out.size()))
                    throw std::runtime_error(
                        "cannot extract zip '" + name +
                        "' entry to memory in '" + _path + "'");
                return out;
            }

            // Iterate every entry, invoking fn(filename, is_dir) for each. fn may call
            // extract_current() to save the current entry to disk.
            template<typename Fn>
            void for_each_entry(Fn&& fn)
            {
                int32_t err = mz_zip_reader_goto_first_entry(_reader);
                if (err == MZ_END_OF_LIST)
                    return;  // empty archive
                if (err != MZ_OK)
                    throw std::runtime_error(
                        "cannot read zip entry in '" + _path + "'");
                while (err == MZ_OK)
                {
                    mz_zip_file* info = nullptr;
                    if (mz_zip_reader_entry_get_info(_reader, &info) != MZ_OK || !info)
                        throw std::runtime_error(
                            "cannot stat zip entry in '" + _path + "'");

                    bool const is_dir = (mz_zip_reader_entry_is_dir(_reader) == MZ_OK);
                    fn(std::string(info->filename ? info->filename : ""), is_dir);

                    err = mz_zip_reader_goto_next_entry(_reader);
                    if (err != MZ_OK && err != MZ_END_OF_LIST)
                        throw std::runtime_error(
                            "cannot advance zip entry in '" + _path + "'");
                }
            }

            // Save the entry the cursor is currently on to a file. Call only from
            // within a for_each_entry callback.
            void extract_current_to_file(std::string const& path)
            {
                if (mz_zip_reader_entry_save_file(_reader, path.c_str()) != MZ_OK)
                    throw std::runtime_error("cannot extract zip entry in '" +
                        _path + "' to '" + path + "'");
            }

        private:
            std::string _path;
            void* _reader = nullptr;
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
            return url; // bare path
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
                    "output path '" + path + "' already exists");
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
                    "error writing '" + path + "': " + e.what());
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
                    "input '" + path  + "' is not a file");
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
                        "output directory '" + output_path.u8string() +
                        "' already exists");
                return nullptr;
            }
        }

        // Read the archive
        std::string json;
        try
        {
            ZipReader zr(path);

            // Read the timeline
            auto json_opt = zr.read_to_string(timeline_file);
            if (!json_opt)
                throw std::runtime_error(
                    "'" + path + "' is missing content.otio");
            json = *json_opt;

            // Extract the archive
            if (options.extract_path.has_value())
            {
                std::filesystem::create_directories(output_path);

                zr.for_each_entry([&](std::string const& filename, bool is_dir)
                {
                    auto const file_path = output_path / std::filesystem::u8path(filename);

                    // Guard against zip slip
                    if (!is_path_safe(output_path, file_path))
                        throw std::runtime_error(
                            "unsafe path '" + filename + "' in '" +
                            path + "'");

                    if (is_dir)
                    {
                        std::filesystem::create_directories(file_path);
                    }
                    else
                    {
                        std::filesystem::create_directories(file_path.parent_path());
                        zr.extract_current_to_file(file_path.u8string());
                    }
                });
            }
        }
        catch (const std::exception& e)
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "error reading '" + path + "': " + e.what());

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
                    "output path '" + path + "' already exists");
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
                    "error writing '" + path + "': " + e.what());
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
                    "input '" + path  + "' is not a directory");
            return nullptr;
        }
        auto const version_path = input_path / version_file;
        if (!std::filesystem::is_regular_file(version_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "'" + path  + "' is missing a version file");
            return nullptr;
        }
        auto const timeline_path = input_path / timeline_file;
        if (!std::filesystem::is_regular_file(timeline_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "'" + path  + "' is missing a timeline file");
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

