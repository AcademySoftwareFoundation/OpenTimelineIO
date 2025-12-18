// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"

#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/urlUtils.h"

#include <unzip.h>
#include <zip.h>

#include <cstdio>
#include <cstring>
#include <fstream>
#include <sstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
namespace bundle {

namespace {

// This class opens and closes a file for I/O.
class FileWrapper
{
public:
    FileWrapper(std::string const& fileName, std::string const& mode)
    {
        _f = fopen(fileName.c_str(), mode.c_str());
    }

    ~FileWrapper()
    {
        if (_f)
        {
            fclose(_f);
            _f = nullptr;
        }
    }

    FILE* operator()() { return _f; }

private:
    FILE* _f = nullptr;
};

// This class writes ZIP files.
class ZipWriter
{
public:
    ZipWriter(std::string const& zip_file_name);

    ~ZipWriter() noexcept(false);

    void add_compressed(
        std::string const& string,
        std::string const& file_name_in_zip);

    void add_uncompressed(
        std::filesystem::path const& path,
        std::string const& file_name_in_zip);

    void close();

private:
    std::string _zip_file_name;
    zipFile _zip = nullptr;
};

ZipWriter::ZipWriter(std::string const& zip_file_name) :
    _zip_file_name(zip_file_name)
{
    // Open the ZIP file.
    _zip = zipOpen64(zip_file_name.c_str(), 0);
    if (!_zip)
    {
        std::stringstream ss;
        ss << "Cannot create ZIP writer: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

ZipWriter::~ZipWriter() noexcept(false)
{
    if (_zip)
    {
        // Close the ZIP file.
        int r = zipClose(_zip, nullptr);
        if (r != ZIP_OK)
        {
            std::stringstream ss;
            ss << "Error closing ZIP file '" << _zip_file_name << "'.";
            throw std::runtime_error(ss.str());
        }
        _zip = nullptr;
    }
}

void
ZipWriter::add_compressed(
    std::string const& content,
    std::string const& file_name_in_zip)
{
    // Add the file to the ZIP.
    zip_fileinfo zfi;
    memset(&zfi, 0, sizeof(zip_fileinfo));
    int r = zipOpenNewFileInZip64(
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
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot add file '" << file_name_in_zip << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }

    // Write the file data to the ZIP.
    r = zipWriteInFileInZip(_zip, content.c_str(), (unsigned int)content.size());
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot write file '" << file_name_in_zip << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }

    // Close the file.
    r = zipCloseFileInZip(_zip);
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Error closing file '" << file_name_in_zip << "' in ZIP.";
        throw std::runtime_error(ss.str());
    }
}

void
ZipWriter::add_uncompressed(
    std::filesystem::path const& path,
    std::string const& file_name_in_zip)
{
    // Add the file to the ZIP.
    zip_fileinfo zfi;
    memset(&zfi, 0, sizeof(zip_fileinfo));
    int r = zipOpenNewFileInZip64(
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
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot add file '" << file_name_in_zip << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }

    // Open the source file.
    FileWrapper f(path.u8string(), "rb");
    if (!f())
    {
        std::stringstream ss;
        ss << "Cannot open file '" << path.u8string() << "'.";
        throw std::runtime_error(ss.str());
    }

    // Get the source file size.
    fseek(f(), 0, SEEK_END);
    if (ferror(f()))
    {
        std::stringstream ss;
        ss << "Cannot seek file '" << path.u8string() << "'.";
        throw std::runtime_error(ss.str());
    }
    const long size = ftell(f());
    fseek(f(), 0, SEEK_SET);
    if (ferror(f()))
    {
        std::stringstream ss;
        ss << "Cannot seek file '" << path.u8string() << "'.";
        throw std::runtime_error(ss.str());
    }

    // Read the source file.
    std::vector<uint8_t> buffer;
    buffer.resize(size);
    size_t count = fread(buffer.data(), size, 1, f());
    if (count != 1)
    {
        std::stringstream ss;
        ss << "Cannot read file '" << path.u8string() << "'.";
        throw std::runtime_error(ss.str());
    }

    // Write the file data to the ZIP.
    r = zipWriteInFileInZip(_zip, buffer.data(), (unsigned int) buffer.size());
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot write file '" << file_name_in_zip << "' to ZIP.";
        throw std::runtime_error(ss.str());
    }

    // Close the file.
    r = zipCloseFileInZip(_zip);
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Error closing file '" << file_name_in_zip << "' in ZIP.";
        throw std::runtime_error(ss.str());
    }
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

// This class reads ZIP files.
class ZipReader
{
public:
    ZipReader(std::string const& zip_file_name);

    ~ZipReader() noexcept(false);

    void extract(std::string const& file_name, std::string&);

    void extract_all(std::string const& output_dir);

private:
    std::string _zip_file_name;
    unzFile _zip = nullptr;
};

ZipReader::ZipReader(std::string const& zip_file_name)
    : _zip_file_name(zip_file_name)
{
    // Open the ZIP file.
    _zip = unzOpen64(zip_file_name.c_str());
    if (!_zip)
    {
        std::stringstream ss;
        ss << "Cannot create ZIP reader: '" << zip_file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

ZipReader::~ZipReader() noexcept(false)
{
    if (_zip)
    {
        // Close the ZIP file.
        int r = unzClose(_zip);
        if (r != ZIP_OK)
        {
            std::stringstream ss;
            ss << "Error closing ZIP reader: '" << _zip_file_name << "'.";
            throw std::runtime_error(ss.str());
        }
        _zip = nullptr;
    }
}

void ZipReader::extract(std::string const& file_name, std::string& text)
{
    // Locate the file in the ZIP.
    int r = unzLocateFile(_zip, file_name.c_str(), 0);
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot locate file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    // Get information about the file in the ZIP.
    unz_file_info64 ufi;
    r = unzGetCurrentFileInfo64(_zip, &ufi, nullptr, 0, nullptr, 0, nullptr, 0);
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot get information for file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    // Open the file in the ZIP.
    r = unzOpenCurrentFile(_zip);
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Cannot open file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    // Read the file in the ZIP.
    text.resize(ufi.uncompressed_size);
    r = unzReadCurrentFile(_zip, text.data(), ufi.uncompressed_size);
    if (r != ufi.uncompressed_size || r < 0)
    {
        std::stringstream ss;
        ss << "Cannot read file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }

    // Close the file.
    r = unzCloseCurrentFile(_zip);
    if (r != ZIP_OK)
    {
        std::stringstream ss;
        ss << "Error closing file in ZIP: '" << file_name << "'.";
        throw std::runtime_error(ss.str());
    }
}

void
ZipReader::extract_all(std::string const& output_dir)
{
    if (unzGoToFirstFile(_zip) == UNZ_OK)
    {
        do
        {
            // Get information about the file in the ZIP.
            unz_file_info64 ufi;
            std::string     file_name;
            file_name.resize(4096); // \todo Is this enough space for paths?
            int r = unzGetCurrentFileInfo64(
                _zip,
                &ufi,
                file_name.data(),
                file_name.size(),
                nullptr,
                0,
                nullptr,
                0);
            if (r != ZIP_OK)
            {
                std::stringstream ss;
                ss << "Cannot get information for file in ZIP: '" << file_name << "'.";
                throw std::runtime_error(ss.str());
            }

            // Open the file in the ZIP.
            r = unzOpenCurrentFile(_zip);
            if (r != ZIP_OK)
            {
                std::stringstream ss;
                ss << "Cannot open file in ZIP: '" << file_name << "'.";
                throw std::runtime_error(ss.str());
            }

            // Read the file in the ZIP.
            std::vector<uint8_t> buf(ufi.uncompressed_size);
            r = unzReadCurrentFile(_zip, buf.data(), ufi.uncompressed_size);
            if (r != ufi.uncompressed_size || r < 0)
            {
                std::stringstream ss;
                ss << "Cannot read file in ZIP: '" << file_name << "'.";
                throw std::runtime_error(ss.str());
            }

            // Close the file.
            r = unzCloseCurrentFile(_zip);
            if (r != ZIP_OK)
            {
                std::stringstream ss;
                ss << "Error closing file in ZIP: '" << file_name << "'.";
                throw std::runtime_error(ss.str());
            }

            // Write the output file.
            const std::filesystem::path path =
                std::filesystem::u8path(output_dir)
                / std::filesystem::u8path(file_name);
            FileWrapper f(path.u8string(), "wb");
            size_t count = fwrite(buf.data(), buf.size(), 1, f());
            if (count != 1)
            {
                std::stringstream ss;
                ss << "Error writing file: '" << path.u8string() << "'.";
                throw std::runtime_error(ss.str());
            }

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

            // Create the directories.
            std::filesystem::create_directory(extract_path);
            std::filesystem::create_directory(extract_path / media_dir);

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
