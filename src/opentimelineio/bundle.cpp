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

#include "miniz.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {
namespace bundle {

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
                [](unsigned char c){ return std::tolower(c); });
            return out;
        }

        // Get a file from a URL
        std::optional<std::string> file_from_url(std::string const& url)
        {
            std::optional<std::string> file;

            constexpr std::string_view file_prefix = "file://";
            if (starts_with(url, file_prefix))
            {
                file = url.substr(file_prefix.size());

                constexpr std::string_view localhost = "localhost/";
                if (starts_with(*file, localhost))
                {
                    file->erase(0, localhost.size() - 1);  // keep leading '/'
                }
            }
            else if (url.find("://") != std::string::npos)
            {
                // Other scheme — not a local file
            }
            else
            {
                file = url;
            }
            
            if (file)
            {
                // Strip query string and fragment
                if (auto pos = file->find('?'); pos != std::string::npos) file->resize(pos);
                if (auto pos = file->find('#'); pos != std::string::npos) file->resize(pos);
                
                // Decode and normalize separators
                *file = percent_decode(*file);
                std::replace(file->begin(), file->end(), '\\', '/');
            }
            
            return file;
        }

        // This struct contains the source path and archive name for each
        // file to be added to the bundle.
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

        // Process all media references according to the policy. The list of
        // paths to be added to the bundle is returned.
        bool process_media_references(
            Timeline*                    timeline,
            std::filesystem::path const& relative_media_path,
            MediaReferencePolicy         policy,
            ErrorStatus*                 error_status,
            BundleFiles&                 out)
        {
            // Store a map of the processed paths to check we are not
            // overwriting any media in the bundle.
            std::map<std::string, std::filesystem::path> paths;
            
            for (auto& clip : timeline->find_clips())
            {
                for (auto& ref : clip->media_references())
                {
                    if (auto ext = dynamic_cast<ExternalReference*>(ref.second))
                    {
                        auto const file = file_from_url(ext->target_url());
                        if (file.has_value())
                        {
                            auto path = std::filesystem::u8path(*file);
                            
                            // Check for overwrites.
                            auto const paths_key = to_lower(path.filename().u8string());
                            auto const i = paths.find(paths_key);
                            if (i != paths.end() &&
                                path.parent_path() != i->second.parent_path())
                            {
                                if (error_status)
                                {
                                    std::stringstream ss;
                                    ss << "media file " << *file <<
                                        " would overwrite " << i->second;
                                    *error_status = ErrorStatus(
                                        ErrorStatus::FILE_WRITE_FAILED,
                                        ss.str());
                                }
                                return false;
                            }
                            paths[paths_key] = path;
                            
                            // Set the URL to the bundle location
                            auto const bundle_path = (std::filesystem::u8path(media_dir) /
                                path.filename()).u8string();
                            ext->set_target_url(bundle_path);

                            // Add the file to be bundled.
                            if (path.is_relative() && !relative_media_path.empty())
                            {
                                path = relative_media_path / path;
                            }
                            out.insert({ path.u8string(), bundle_path });
                        }
                    }
                }
            }
            return true;
        }
        
        // Common code for preparing the bundle.
        bool prepare_bundle(
            Timeline const*                         timeline,
            WriteOptions const&                     options,
            ErrorStatus*                            error_status,
            SerializableObject::Retainer<Timeline>& out_clone,
            std::string&                            out_json,
            BundleFiles&                            out_files)
        {
            out_clone = SerializableObject::Retainer<Timeline>(
                dynamic_cast<Timeline*>(timeline->clone(error_status)));
            if (!out_clone || is_error(error_status))
                return false;
           
            std::filesystem::path relative_media_path;
            if (options.relative_media_path.has_value())
                relative_media_path = std::filesystem::u8path(*options.relative_media_path);
           
            if (!process_media_references(
                out_clone,
                relative_media_path,
                options.policy,
                error_status,
                out_files))
                return false;
           
           out_json = out_clone->to_json_string(error_status);
           return !is_error(error_status);
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
            
            mz_zip_archive_file_stat stat(mz_uint i)
            {
                mz_zip_archive_file_stat s;
                if (!mz_zip_reader_file_stat(&_zip, i, &s))
                {
                    throw std::runtime_error("cannot stat zip entry");
                }
                return s;
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

    bool write_otioz(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options,
        ErrorStatus*        error_status)
    {
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
        std::string const& output_dir,
        ErrorStatus*       error_status)
    {
        auto const input_path = std::filesystem::u8path(path);
        if (!std::filesystem::is_regular_file(input_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    "input path is not a file");
            return nullptr;
        }
        auto const output_path = std::filesystem::u8path(output_dir);
        if (std::filesystem::exists(output_path))
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_WRITE_FAILED,
                    "output directory already exists");
            return nullptr;
        }

        // Extract the archive
        try
        {
            std::filesystem::create_directories(output_path);
            
            ZipReader zr(path);
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
        catch (const std::exception& e)
        {
            if (error_status)
                *error_status = ErrorStatus(
                    ErrorStatus::FILE_OPEN_FAILED,
                    e.what());

            // Try and remove the directory if it was partially written
            std::error_code ec;
            std::filesystem::remove_all(output_path, ec);
            return nullptr;
        }

        return Timeline::from_json_file(output_path.u8string(), error_status);
    }

    bool write_otiod(
        Timeline const*     timeline,
        std::string const&  path,
        WriteOptions const& options,
        ErrorStatus*        error_status)
    {
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
        ErrorStatus*       error_status)
    {
        // Validate the directory structure
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
        
        // Read and parse the timeline
        return Timeline::from_json_file(timeline_path.u8string(), error_status);
    }
}
}
}

