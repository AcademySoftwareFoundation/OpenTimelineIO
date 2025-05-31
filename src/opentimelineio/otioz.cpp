// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/timeline.h"

#include <mz.h>
#include <mz_os.h>
#include <mz_strm.h>
#include <mz_zip.h>
#include <mz_zip_rw.h>

#include <filesystem>
#include <fstream>
#include <sstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace bundle {

namespace {

class ZipWriter
{
public:
    ZipWriter(std::string const& zip_file_name);
    ~ZipWriter();

    void add_compressed(
        std::string const& string,
        std::string const& file_name_in_zip);

    void add_uncompressed(
        std::filesystem::path const& path,
        std::string const& file_name_in_zip);

 private:
    void* _zip = nullptr;
};

ZipWriter::ZipWriter(std::string const& zip_file_name)
{
    _zip = mz_zip_writer_create();
    if (!_zip)
    {
        std::stringstream ss;
        ss << "Cannot create ZIP writer: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    int32_t err = mz_zip_writer_open_file(_zip, zip_file_name.c_str(), 0, 0);
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot open ZIP file: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

ZipWriter::~ZipWriter()
{
    if (_zip)
    {
        mz_zip_writer_close(_zip);
        mz_zip_writer_delete(&_zip);
    }
}

void
ZipWriter::add_compressed(
    std::string const& content,
    std::string const& file_name_in_zip)
{
    mz_zip_file file_info;
    memset(&file_info, 0, sizeof(mz_zip_file));
    mz_zip_writer_set_compress_level(_zip, MZ_COMPRESS_LEVEL_NORMAL);
    file_info.version_madeby     = MZ_VERSION_MADEBY;
    file_info.flag               = MZ_ZIP_FLAG_UTF8;
    file_info.modified_date      = std::time(nullptr);
    file_info.compression_method = MZ_COMPRESS_METHOD_DEFLATE;
    file_info.filename           = file_name_in_zip.c_str();
    int32_t err                  = mz_zip_writer_add_buffer(
        _zip,
        (void*)(content.c_str()),
        (int32_t)(content.size()),
        &file_info);
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot add file '" << file_name_in_zip << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }
}

void
ZipWriter::add_uncompressed(
    std::filesystem::path const& path,
    std::string const& file_name_in_zip)
{
    mz_zip_writer_set_compress_method(_zip, MZ_COMPRESS_METHOD_STORE);
    int32_t err = mz_zip_writer_add_file(
        _zip,
        path.u8string().c_str(),
        file_name_in_zip.c_str());
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot add file '" << path.u8string() << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }
}

} // namespace

bool
to_otioz(
    Timeline const*           timeline,
    std::string const&        timeline_dir,
    std::string const&        file_name,
    MediaReferencePolicy      media_reference_policy,
    ErrorStatus*              error_status,
    schema_version_map const* target_family_label_spec,
    int                       indent)
{
    // Check that the path does not exist.
    std::filesystem::path const path = std::filesystem::u8path(file_name);
    if (std::filesystem::exists(path))
    {
        if (error_status)
        {
            std::stringstream ss;
            ss << "'" << path.u8string() << "' exists, will not overwrite.";
            *error_status =
                ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, ss.str());
        }
        return false;
    }

    // General algorithm for the file bundles:
    //
    // * Build the file manifest (list of paths to files on disk that will be
    //   put into the archive).
    // * Build a mapping of path to file on disk to url to put into the media
    //   reference in the result.
    // * Relink the media references to point at the final location inside the
    //   archive.
    // * Build the resulting structure (zip file, directory).
    std::map<
        std::string,
        std::vector<SerializableObject::Retainer<ExternalReference>>>
        path_to_mr_map;
    ErrorStatus error_status_tmp;
    auto result_timeline = timeline_for_bundle_and_manifest(
        timeline,
        timeline_dir,
        media_reference_policy,
        path_to_mr_map,
        error_status_tmp);
    if (is_error(error_status_tmp))
    {
        if (error_status)
        {
            *error_status = error_status_tmp;
        }
        return false;
    }

    // Relink all the media references to their target paths.
    std::map<std::filesystem::path, std::string>
        abspath_to_output_path_map;
    for (auto const& i: path_to_mr_map)
    {
        std::filesystem::path const target =
            std::filesystem::u8path(media_dir) /
            std::filesystem::u8path(i.first).filename();

        // Conform to POSIX style paths inside the bundle, so that they are
        // portable between windows and UNIX style environments.
        std::string const final_path = to_unix_separators(target.u8string());

        // Cache the output path.
        abspath_to_output_path_map[i.first] = final_path;

        for (auto const& mr : i.second)
        {
            // Convert the path to a URL and set the media reference.
            std::string const url = url_from_filepath(final_path);
            mr->set_target_url(url);
        }
    }

    // Create the .otio.
    std::string const result_otio = result_timeline->to_json_string(
        error_status,
        target_family_label_spec,
        indent);
    if (error_status && is_error(error_status))
    {
        return false;
    }

    // Write the archive.
    try
    {
        ZipWriter zip(file_name);

        // Write the .otio file.
        zip.add_compressed(result_otio, otio_file);

        // Write the version file.
        zip.add_compressed(otioz_version, version_file);

        // Write the media files.
        for (auto const& i: abspath_to_output_path_map)
        {
            zip.add_uncompressed(i.first, i.second);
        }
    }
    catch (std::exception const& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, e.what());
        }
        return false;
    }

    return true;
}

namespace {

class ZipReader
{
public:
    ZipReader(
        std::string const& zip_file_name,
        std::string const& output_dir);
    ~ZipReader();

private:
    void* _zip = nullptr;
};

ZipReader::ZipReader(
    std::string const& zip_file_name,
    std::string const& output_dir)
{
    _zip = mz_zip_reader_create();
    if (!_zip)
    {
        std::stringstream ss;
        ss << "Cannot create ZIP reader: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    int32_t err = mz_zip_reader_open_file(_zip, zip_file_name.c_str());
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot open ZIP file: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    err = mz_zip_reader_save_all(_zip, output_dir.c_str());
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot extract ZIP file: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

ZipReader::~ZipReader()
{
    if (_zip)
    {
        mz_zip_reader_close(_zip);
        mz_zip_reader_delete(&_zip);
    }
}

} // namespace

std::pair<SerializableObject::Retainer<Timeline>, std::string>
from_otioz(
    std::string const& file_name,
    std::string const& output_dir,
    ErrorStatus*       error_status)
{
    std::pair<SerializableObject::Retainer<Timeline>, std::string> out;

    // Check that the output directory does not exist.
    std::filesystem::path const path = std::filesystem::u8path(output_dir);
    if (std::filesystem::exists(path))
    {
        if (error_status)
        {
            std::stringstream ss;
            ss << "'" << path.u8string() << "' exists, will not overwrite.";
            *error_status =
                ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, ss.str());
        }
        return out;
    }

    // Read the archive.
    try
    {
        ZipReader(file_name, output_dir);

        std::string const timeline_file_name =
            (std::filesystem::u8path(output_dir)
             / std::filesystem::u8path(otio_file))
                .u8string();
        out = std::make_pair(
            dynamic_cast<Timeline*>(
                Timeline::from_json_file(timeline_file_name, error_status)),
            timeline_file_name);
    }
    catch (std::exception const& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, e.what());
        }
    }

    return out;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
