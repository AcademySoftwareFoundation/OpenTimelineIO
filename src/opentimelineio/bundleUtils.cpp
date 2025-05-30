// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundleUtils.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/missingReference.h"

#include <algorithm>
#include <filesystem>
#include <iomanip>
#include <regex>
#include <sstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace bundle {

std::string
to_string(MediaReferencePolicy media_referenece_policy)
{
    switch (media_referenece_policy)
    {
        case MediaReferencePolicy::ErrorIfNotFile:
            return "ErrorIfNotFile";
        case MediaReferencePolicy::MissingIfNotFile:
            return "MissingIfNotFile";
        case MediaReferencePolicy::AllMissing:
            return "AllMissing";
        default:
            break;
    }
    return "";
}

std::string
to_unix_separators(const std::string& path)
{
    std::string result = path;
    std::replace(result.begin(), result.end(), '\\', '/');
    return result;
}

std::string
scheme_from_url(std::string const& url)
{
    std::regex const rx("^([A-Za-z0-9+-\\.]+://)");
    auto const       rxi = std::sregex_iterator(url.begin(), url.end(), rx);
    return rxi != std::sregex_iterator() ? rxi->str() : std::string();
}

namespace {

std::string
url_encode(std::string const& url)
{
    // Don't encode these characters.
    const std::vector<char> chars = { '-', '.', '_', '~', ':', '/', '?',  '#',
                                      '[', ']', '@', '!', '$', '&', '\'', '(',
                                      ')', '*', '+', ',', ';', '=', '\\' };

    // Copy characters to the result, encoding if necessary.
    std::stringstream ss;
    ss.fill('0');
    ss << std::hex;
    for (auto i = url.begin(), end = url.end(); i != end; ++i)
    {
        const auto j = std::find(chars.begin(), chars.end(), *i);
        if (std::isalnum(*i) || j != chars.end())
        {
            ss << *i;
        }
        else
        {
            ss << '%' << std::setw(2) << int(*i);
        }
    }
    return ss.str();
}

std::string
url_decode(std::string const& url)
{
    std::string result;

    // Find all percent encodings.
    size_t           url_pos = 0;
    const std::regex rx("(%[0-9A-Fa-f][0-9A-Fa-f])");
    for (auto i = std::sregex_iterator(url.begin(), url.end(), rx);
         i != std::sregex_iterator();
         ++i)
    {

        // Copy parts without any encodings.
        if (url_pos != static_cast<size_t>(i->position()))
        {
            result.append(url.substr(url_pos, i->position() - url_pos));
            url_pos = i->position() + i->str().size();
        }

        // Convert the encoding and append it.
        std::stringstream ss;
        ss << std::hex << i->str().substr(1);
        unsigned int j = 0;
        ss >> j;
        result.push_back(char(j));
    }

    // Copy the remainder without any encodings.
    if (!url.empty() && url_pos != url.size() - 1)
    {
        result.append(url.substr(url_pos, url.size() - url_pos));
    }

    return result;
}

} // namespace

std::string
url_from_filepath(std::string const& filepath)
{
    const std::string encoded = url_encode(to_unix_separators(filepath));
    const std::string url     = std::filesystem::u8path(filepath).is_relative()
                                    ? encoded
                                    : ("file://" + encoded);
    return url;
}

std::string
filepath_from_url(std::string const& url)
{
    // Skip over the URL scheme.
    bool              has_scheme = false;
    size_t            pos        = 0;
    std::string const scheme     = scheme_from_url(url);
    if (!scheme.empty())
    {
        has_scheme = true;
        pos += scheme.size();
    }

    // Remove the URL query and fragment.
    size_t size = std::string::npos;
    size_t i    = url.find('?', pos);
    size_t j    = url.find('#', pos);
    if (i != std::string::npos || j != std::string::npos)
    {
        size = std::min(i, j) + 1;
    }
    const std::string path = url.substr(pos, size);

    // Decode the path.
    std::string decoded = url_decode(path);

    // Use UNIX separators.
    decoded = to_unix_separators(decoded);

    // Check for Windows drive letters.
    bool        has_windows_drive = false;
    std::regex  rx                = std::regex("^([A-Za-z]:)");
    std::smatch matches;
    if (std::regex_search(decoded, matches, rx))
    {
        has_windows_drive = true;
    }
    else
    {
        rx = std::regex("^(.*/)([A-Za-z]:)");
        if (std::regex_search(decoded, matches, rx))
        {
            has_windows_drive = true;
            decoded = decoded.substr(matches.position(1) + matches.length(1));
        }
    }

    // Add the "//" for UNC paths.
    bool has_unc = false;
    size         = decoded.size();
    if (has_scheme && !has_windows_drive && pos < size - 1 && decoded[0] != '/')
    {
        has_unc = true;
        decoded.insert(0, "//");
    }

    // Remove the current directory.
    rx = std::regex("^(./)");
    if (!has_windows_drive && !has_unc
        && std::regex_search(decoded, matches, rx))
    {
        decoded = decoded.substr(matches.position() + matches.length());
    }

    return decoded;
}

namespace {

// Replace the original media reference with a missing reference with the same
// metadata.
//
// Also adds original_target_url and missing_reference_because fields.
SerializableObject::Retainer<MediaReference>
reference_cloned_and_missing(
    SerializableObject::Retainer<ExternalReference> const& orig_mr,
    std::string const&                                     reason_missing)
{
    SerializableObject::Retainer<MediaReference> result(
        new MissingReference);
    auto metadata = orig_mr->metadata();
    metadata["missing_reference_because"] = reason_missing;
    metadata["original_target_url"]       = orig_mr->target_url();
    return result;
}

bool
guarantee_unique_basenames(
    std::vector<std::string> const& path_list,
    ErrorStatus& error_status)
{
    // Walking across all unique file references, guarantee that all the
    // basenames are unique.
    std::map<std::string, std::string> basename_to_source_fn;
    for (auto const& fn : path_list)
    {
        std::string const new_basename =
            std::filesystem::u8path(fn).filename().u8string();
        auto i = basename_to_source_fn.find(new_basename);
        if (i != basename_to_source_fn.end())
        {
            std::stringstream ss;
            ss << "Bundles require that the media files have unique "
               << "basenames. File '" << fn << "' and '"
               << i->second << "' have matching basenames of: '"
               << new_basename << "'.";
            error_status =
                ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, ss.str());
            return false;
        }
        basename_to_source_fn[new_basename] = fn;
    }
    return true;
}

}

SerializableObject::Retainer<Timeline> timeline_for_bundle_and_manifest(
    SerializableObject::Retainer<Timeline> const& timeline,
    std::string const&                            timeline_dir,
    MediaReferencePolicy                          media_reference_policy,
    std::map<
        std::string,
        std::vector<SerializableObject::Retainer<ExternalReference>>>&
                 path_to_reference_map,
    ErrorStatus& error_status)
{
    // Make an editable copy of the timeline.
    SerializableObject::Retainer<Timeline> result_timeline(
        dynamic_cast<Timeline*>(timeline->clone()));

    path_to_reference_map.clear();
    std::set<std::filesystem::path> invalid_files;

    // The result timeline is manipulated in place.
    for (auto& cl : result_timeline->find_clips())
    {
        if (auto mr = dynamic_cast<ExternalReference*>(cl->media_reference()))
        {
            if (MediaReferencePolicy::AllMissing == media_reference_policy)
            {
                std::stringstream ss;
                ss << to_string(media_reference_policy)
                   << " specified as the MediaReferencePolicy ";
                cl->set_media_reference(
                    reference_cloned_and_missing(mr, ss.str()));
                continue;
            }

            // Ensure that the URL scheme is either "file://" or "".
            // File means "absolute path", "" is interpreted as a relative path,
            // relative to the source .otio file.
            std::string const scheme = scheme_from_url(mr->target_url());
            if (!(scheme == "file://" || scheme.empty()))
            {
                if (MediaReferencePolicy::ErrorIfNotFile == media_reference_policy)
                {
                    std::stringstream ss;
                    ss << "Bundles only work with media reference target URLs "
                       << "that begin with 'file://' or ''. Got a target URL of: "
                       << mr->target_url();
                    error_status =
                        ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, ss.str());
                    return result_timeline;
                }
                if (MediaReferencePolicy::MissingIfNotFile == media_reference_policy)
                {
                    cl->set_media_reference(reference_cloned_and_missing(
                        mr,
                        "target_url is not a file scheme url"));
                    continue;
                }
            }

            // Get an absolute path to the target file.
            std::filesystem::path target_file =
                std::filesystem::u8path(filepath_from_url(mr->target_url()));
            if (scheme.empty())
            {
                target_file = std::filesystem::u8path(timeline_dir) / target_file;
            }
            target_file = std::filesystem::absolute(target_file);

            // If the file hasn't already been checked.
            auto i = path_to_reference_map.find(target_file.u8string());
            auto j = invalid_files.find(target_file);
            if (i == path_to_reference_map.end() &&
                j == invalid_files.end() &&
                (!std::filesystem::exists(target_file) ||
                    !std::filesystem::is_regular_file(target_file)))
            {
                invalid_files.insert(target_file);
            }

            j = invalid_files.find(target_file);
            if (j != invalid_files.end())
            {
                if (MediaReferencePolicy::ErrorIfNotFile == media_reference_policy)
                {
                    std::stringstream ss;
                    ss << target_file << " is not a file or does not exist.";
                    error_status = ErrorStatus(
                        ErrorStatus::FILE_WRITE_FAILED,
                        ss.str());
                    return result_timeline;
                }
                if (MediaReferencePolicy::MissingIfNotFile == media_reference_policy)
                {
                    cl->set_media_reference(reference_cloned_and_missing(
                        mr,
                        "target_url target is not a file or does not exist"));
                    // Do not need to relink it in the future or add this target to
                    // the manifest, because the path is either not a file or does
                    // not exist.
                    continue;
                }
            }

            // Add the media reference to the list of references that point at
            // this file, they will need to be relinked.
            path_to_reference_map[target_file.u8string()].push_back(mr);
        }
    }

    std::vector<std::string> path_list;
    for (auto const& i : path_to_reference_map)
    {
        path_list.push_back(i.first);
    }
    guarantee_unique_basenames(path_list, error_status);

    return result_timeline;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
