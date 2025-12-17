// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/urlUtils.h"

/*#include <mz.h>
#include <mz_os.h>
#include <mz_strm.h>
#include <mz_zip.h>
#include <mz_zip_rw.h>*/
#include <unzip.h>
#include <zip.h>

#include <cstdio>
#include <cstring>
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
    //void* _zip = nullptr;
    //uint32_t _attributes = 0;
     zipFile _zip = nullptr;
};

ZipWriter::ZipWriter(std::string const& zip_file_name)
{
    /*_zip = mz_zip_writer_create();
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

    err = mz_os_get_file_attribs(zip_file_name.c_str(), &_attributes);
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot get file attributes: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }*/
    _zip = zipOpen64(zip_file_name.c_str(), 0);
    if (!_zip)
    {
        std::stringstream ss;
        ss << "Cannot create ZIP writer: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

ZipWriter::~ZipWriter()
{
    if (_zip)
    {
        //mz_zip_writer_close(_zip);
        //mz_zip_writer_delete(&_zip);
        zipClose(_zip, nullptr);
    }
}

void
ZipWriter::add_compressed(
    std::string const& content,
    std::string const& file_name_in_zip)
{
    /*mz_zip_file file_info;
    memset(&file_info, 0, sizeof(mz_zip_file));
    mz_zip_writer_set_compress_level(_zip, MZ_COMPRESS_LEVEL_NORMAL);
    file_info.version_madeby     = MZ_VERSION_MADEBY;
    file_info.flag               = MZ_ZIP_FLAG_UTF8;
    file_info.modified_date      = std::time(nullptr);
    file_info.compression_method = MZ_COMPRESS_METHOD_DEFLATE;
    file_info.uncompressed_size  = content.size();
    file_info.filename           = file_name_in_zip.c_str();
    file_info.external_fa        = _attributes;
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
    }*/

    zip_fileinfo zfi;
    memset(&zfi, 0, sizeof(zip_fileinfo));
    zipOpenNewFileInZip64(
        _zip,
        file_name_in_zip.c_str(),
        &zfi,
        nullptr,
        0,
        nullptr,
        0,
        nullptr,
        Z_DEFLATED,
        Z_DEFAULT_COMPRESSION,
        1);
    zipWriteInFileInZip(_zip, content.c_str(), (unsigned int)content.size());
    zipCloseFileInZip(_zip);
}

void
ZipWriter::add_uncompressed(
    std::filesystem::path const& path,
    std::string const& file_name_in_zip)
{
    /*mz_zip_writer_set_compress_method(_zip, MZ_COMPRESS_METHOD_STORE);
    int32_t err = mz_zip_writer_add_file(
        _zip,
        path.u8string().c_str(),
        file_name_in_zip.c_str());
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot add file '" << path.u8string() << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }*/

    zip_fileinfo zfi;
    memset(&zfi, 0, sizeof(zip_fileinfo));
    zipOpenNewFileInZip64(
        _zip,
        file_name_in_zip.c_str(),
        &zfi,
        nullptr,
        0,
        nullptr,
        0,
        nullptr,
        0,
        0,
        1);
    FILE* f = fopen(path.u8string().c_str(), "rb");
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::vector<uint8_t> buffer;
    buffer.resize(size);
    fread(buffer.data(), size, 1, f);
    fclose(f);
    zipWriteInFileInZip(_zip, buffer.data(), (unsigned int) buffer.size());
    zipCloseFileInZip(_zip);
}

} // namespace

bool
to_otioz(
    Timeline const*     timeline,
    std::string const&  file_name,
    WriteOptions const& options,
    ErrorStatus*        error_status)
{
    try
    {
        // Check the path does not already exist.
        std::filesystem::path const path = std::filesystem::u8path(file_name);
        if (std::filesystem::exists(path))
        {
            std::stringstream ss;
            ss << "'" << path.u8string() << "' exists, will not overwrite.";
            throw std::runtime_error(ss.str());
        }

        // Create the new timeline and file manifest.
        Manifest manifest;
        auto result_timeline = timeline_for_bundle_and_manifest(
            timeline,
            std::filesystem::u8path(options.parent_path),
            options.media_policy,
            manifest);

        // Write the archive.
        ZipWriter zip(file_name);

        // Write the version file.
        zip.add_compressed(otioz_version, version_file);

        // Write the .otio file.
        std::string const result_otio = result_timeline->to_json_string(
            error_status,
            options.target_family_label_spec,
            options.indent);
        if (error_status && is_error(error_status))
        {
            throw std::runtime_error(error_status->details);
        }
        zip.add_compressed(result_otio, otio_file);

        // Write the files from the manifest.
        for (auto const& i: manifest)
        {
            zip.add_uncompressed(i.first, i.second.u8string());
        }
    }
    catch (std::exception const& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::BUNDLE_WRITE_ERROR, e.what());
        }
        return false;
    }
    return true;
}

namespace {

class ZipReader
{
public:
    ZipReader(std::string const& zip_file_name);
    ~ZipReader();

    void extract(std::string const& file_name, std::string&);

    void extract_all(std::string const& output_dir);

private:
    std::string _zip_file_name;
    //void* _zip = nullptr;
    unzFile _zip = nullptr;
};

ZipReader::ZipReader(std::string const& zip_file_name)
    : _zip_file_name(zip_file_name)
{
    /*_zip = mz_zip_reader_create();
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
    }*/

    _zip = unzOpen64(zip_file_name.c_str());
    if (!_zip)
    {
        std::stringstream ss;
        ss << "Cannot create ZIP writer: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

ZipReader::~ZipReader()
{
    if (_zip)
    {
        //mz_zip_reader_close(_zip);
        //mz_zip_reader_delete(&_zip);
        unzClose(_zip);
    }
}

void ZipReader::extract(std::string const& file_name, std::string& text)
{
    /*int32_t err = mz_zip_reader_locate_entry(_zip, file_name.c_str(), 0);
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot locate file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    int32_t const size = mz_zip_reader_entry_save_buffer_length(_zip);
    text.resize(size);
    err = mz_zip_reader_entry_save_buffer(_zip, text.data(), size);
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot read file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }*/

    unzLocateFile(_zip, file_name.c_str(), 0);
    unz_file_info64 ufi; 
    unzGetCurrentFileInfo64(_zip, &ufi, nullptr, 0, nullptr, 0, nullptr, 0);
    unzOpenCurrentFile(_zip);
    text.resize(ufi.uncompressed_size);
    unzReadCurrentFile(_zip, text.data(), ufi.uncompressed_size);
    unzCloseCurrentFile(_zip);
}

void
ZipReader::extract_all(std::string const& output_dir)
{
    /*int32_t err = mz_zip_reader_save_all(_zip, output_dir.c_str());
    if (err != MZ_OK)
    {
        std::stringstream ss;
        ss << "Cannot extract ZIP file: '" << _zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }*/

    if (unzGoToFirstFile(_zip) == UNZ_OK)
    {
        do
        {
            unz_file_info64 ufi;
            std::string     fileName;
            fileName.resize(1024);
            unzGetCurrentFileInfo64(
                _zip,
                &ufi,
                fileName.data(),
                fileName.size(),
                nullptr,
                0,
                nullptr,
                0);
            unzOpenCurrentFile(_zip);
            std::vector<uint8_t> buf(ufi.uncompressed_size);
            unzReadCurrentFile(_zip, buf.data(), ufi.uncompressed_size);
            unzCloseCurrentFile(_zip);
            const std::filesystem::path path =
                std::filesystem::u8path(output_dir)
                / std::filesystem::u8path(fileName);
            const std::filesystem::path parentPath = path.parent_path();
            if (!std::filesystem::exists(parentPath))
            {
                std::filesystem::create_directory(parentPath);
            }
            FILE* f = fopen(path.u8string().c_str(), "wb");
            fwrite(buf.data(), buf.size(), 1, f);
            fclose(f);

        } while (unzGoToNextFile(_zip) == UNZ_OK);
    }
}

} // namespace

Timeline*
from_otioz(
    std::string const&      file_name,
    OtiozReadOptions const& options,
    ErrorStatus*            error_status)
{
    Timeline* timeline = nullptr;
    try
    {
        // Open the archive.
        ZipReader zip(file_name);

        if (!options.extract_path.empty())
        {
            // Check the path does not already exist.
            std::filesystem::path const extract_path =
                std::filesystem::u8path(options.extract_path);
            if (std::filesystem::exists(extract_path))
            {
                std::stringstream ss;
                ss << "'" << extract_path.u8string()
                   << "' exists, will not overwrite.";
                throw std::runtime_error(ss.str());
            }
            std::filesystem::create_directory(extract_path);

            // Extract the archive.
            zip.extract_all(extract_path.u8string());

            // Read the timeline.
            std::string const timeline_file =
                (extract_path / otio_file).u8string();
            timeline = dynamic_cast<Timeline*>(
                Timeline::from_json_file(timeline_file, error_status));
        }
        else
        {
            // Extract and read the timeline.
            std::string json;
            zip.extract(otio_file, json);
            timeline = dynamic_cast<Timeline*>(
                Timeline::from_json_string(json, error_status));
        }
    }
    catch (std::exception const& e)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::BUNDLE_READ_ERROR, e.what());
        }
    }
    return timeline;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
