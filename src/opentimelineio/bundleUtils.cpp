// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundleUtils.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/missingReference.h"
#include "opentimelineio/imageSequenceReference.h"

#include <algorithm>
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
to_unix_separators(std::string const& path)
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

std::string
url_encode(std::string const& url)
{
    // Don't encode these characters.
    std::vector<char> const chars = { '-', '.', '_', '~', ':', '/', '?',  '#',
                                      '[', ']', '@', '!', '$', '&', '\'', '(',
                                      ')', '*', '+', ',', ';', '=', '\\' };

    // Copy characters to the result, encoding if necessary.
    std::stringstream ss;
    ss.fill('0');
    ss << std::hex;
    for (auto i = url.begin(), end = url.end(); i != end; ++i)
    {
        auto const j = std::find(chars.begin(), chars.end(), *i);
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
    std::regex const rx("(%[0-9A-Fa-f][0-9A-Fa-f])");
    for (auto i = std::sregex_iterator(url.begin(), url.end(), rx);
         i != std::sregex_iterator();
         ++i)
    {
        // Copy parts without any encodings.
        if (url_pos != static_cast<size_t>(i->position()))
        {
            result.append(url.substr(url_pos, i->position() - url_pos));
            url_pos = i->position();
        }

        // Convert the encoding and append it.
        std::stringstream ss;
        ss << std::hex << i->str().substr(1);
        unsigned int j = 0;
        ss >> j;
        result.push_back(char(j));
        url_pos += i->str().size();
    }

    // Copy the remainder without any encodings.
    if (!url.empty() && url_pos != url.size() - 1)
    {
        result.append(url.substr(url_pos, url.size() - url_pos));
    }

    return result;
}

std::string
url_from_filepath(std::string const& filepath)
{
    std::string const encoded = url_encode(to_unix_separators(filepath));
    std::string const url = std::filesystem::u8path(filepath).is_relative()
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
    std::string const path = url.substr(pos, size);

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

// Replace the original media reference with a missing reference with the
// same metadata.
// 
// Aditional metadata:
// * missing_reference_because
// 
// For external references:
// * original_target_url
//
// For image sequence references:
// * original_target_url_base
// * original_name_prefix
// * original_name_suffix
// * original_start_frame
// * original_frame_step
// * original_rate
// * original_frame_zero_padding
SerializableObject::Retainer<MediaReference>
reference_cloned_and_missing(
    SerializableObject::Retainer<MediaReference> const& orig_mr,
    std::string const&                                  reason_missing)
{
    SerializableObject::Retainer<MediaReference> result(new MissingReference);
    auto                                         metadata = orig_mr->metadata();
    metadata["missing_reference_because"]                 = reason_missing;
    if (auto orig_er = dynamic_retainer_cast<ExternalReference>(orig_mr))
    {
        metadata["original_target_url"] = orig_er->target_url();
    }
    else if (auto orig_isr = dynamic_retainer_cast<ImageSequenceReference>(orig_mr))
    {
        metadata["original_target_url_base"] = orig_isr->target_url_base();
        metadata["original_name_prefix"]     = orig_isr->name_prefix();
        metadata["original_name_suffix"]     = orig_isr->name_suffix();
        metadata["original_start_frame"]     = orig_isr->start_frame();
        metadata["original_frame_step"]      = orig_isr->frame_step();
        metadata["original_rate"]            = orig_isr->rate();
        metadata["original_frame_zero_padding"] =
            orig_isr->frame_zero_padding();
    }
    return result;
}

} // namspace

SerializableObject::Retainer<Timeline> timeline_for_bundle_and_manifest(
    SerializableObject::Retainer<Timeline> const& timeline,
    std::filesystem::path const&                  timeline_dir,
    MediaReferencePolicy                          media_reference_policy,
    std::map<std::filesystem::path, std::filesystem::path>& manifest)
{
    manifest.clear();
    std::map<std::filesystem::path, std::filesystem::path>
        bundle_paths_to_abs_paths;

    // Make an editable copy of the timeline.
    SerializableObject::Retainer<Timeline> result_timeline(
        dynamic_cast<Timeline*>(timeline->clone()));

    // The result timeline is manipulated in place.
    for (auto& cl : result_timeline->find_clips())
    {
        auto mr  = cl->media_reference();
        auto er  = dynamic_cast<ExternalReference*>(cl->media_reference());
        auto isr = dynamic_cast<ImageSequenceReference*>(cl->media_reference());
        if (er || isr)
        {
            if (MediaReferencePolicy::AllMissing == media_reference_policy)
            {
                std::stringstream ss;
                ss << to_string(media_reference_policy)
                   << " specified as the MediaReferencePolicy";
                cl->set_media_reference(
                    reference_cloned_and_missing(mr, ss.str()));
                continue;
            }

            // Ensure that the URL scheme is either "file://" or "".
            // File means "absolute path", "" is interpreted as a relative path,
            // relative to the source .otio file.
            std::string const url    = er ? er->target_url()
                                          : isr->target_url_base();
            std::string const scheme = scheme_from_url(url);
            if (!(scheme == "file://" || scheme.empty()))
            {
                if (MediaReferencePolicy::ErrorIfNotFile == media_reference_policy)
                {
                    std::stringstream ss;
                    ss << "Bundles only work with media reference target URLs "
                       << "that begin with 'file://' or ''. Got a target URL of: "
                       << "'" << url << "'.";
                    throw std::runtime_error(ss.str());
                }
                if (MediaReferencePolicy::MissingIfNotFile == media_reference_policy)
                {
                    cl->set_media_reference(reference_cloned_and_missing(
                        mr,
                        "target_url is not a file scheme url"));
                    continue;
                }
            }

            // Get the list of target files.
            std::vector<std::string> target_files;
            if (er)
            {
                target_files.push_back(filepath_from_url(er->target_url()));
            }
            else if (isr)
            {
                TimeRange const range = cl->available_range();
                for (int frame = range.start_time().to_frames();
                     frame <= range.duration().to_frames();
                     ++frame)
                {
                    std::stringstream ss;
                    ss << isr->name_prefix();
                    ss << std::setfill('0')
                       << std::setw(isr->frame_zero_padding()) << frame;
                    ss << isr->name_suffix();
                    target_files.push_back(filepath_from_url(
                        isr->target_url_base() + "/" + ss.str()));
                }
            }

            // Get absolute paths to the target files.
            std::vector<std::filesystem::path> target_paths;
            std::filesystem::path              target_path;
            bool                               target_error = false;
            for (const auto& target_file: target_files)
            {
                target_path = std::filesystem::u8path(target_file);
                if (scheme.empty())
                {
                    target_path = timeline_dir / target_path;
                }
                target_path = std::filesystem::absolute(target_path);
                if (!std::filesystem::exists(target_path)
                    || !std::filesystem::is_regular_file(target_path))
                {
                    target_error = true;
                    break;
                }
                target_paths.push_back(target_path);
            }
            if (target_error)
            {
                if (MediaReferencePolicy::ErrorIfNotFile
                    == media_reference_policy)
                {
                    std::stringstream ss;
                    ss << "'" << target_path.u8string()
                       << "' is not a file or does not exist.";
                    throw std::runtime_error(ss.str());
                }
                if (MediaReferencePolicy::MissingIfNotFile
                    == media_reference_policy)
                {
                    cl->set_media_reference(reference_cloned_and_missing(
                        mr,
                        "target_url target is not a file or does not exist"));
                    continue;
                }
            }

            // Add files to the manifest.
            std::filesystem::path bundle_path;
            for (auto const& path: target_paths)
            {
                bundle_path = media_dir / path.filename();
                const auto i = manifest.find(path);
                if (i == manifest.end())
                {
                    const auto j = bundle_paths_to_abs_paths.find(bundle_path);
                    if (j != bundle_paths_to_abs_paths.end())
                    {
                        std::stringstream ss;
                        ss << "Bundles require that the media files have unique "
                           << "basenames. File '" << path.u8string()
                           << "' and '" << i->second
                           << "' have matching basenames of: '"
                           << path.filename().u8string() << "'.";
                        throw std::runtime_error(ss.str());
                    }
                    bundle_paths_to_abs_paths[bundle_path] = path;
                    manifest[path] = bundle_path;
                }
            }

            // Relink the media reference.
            if (er)
            {
                std::string const new_url =
                    url_from_filepath(bundle_path.u8string());
                er->set_target_url(new_url);
            }
            else if (isr)
            {
                std::string const new_url =
                    url_from_filepath(bundle_path.parent_path().u8string())
                    + "/";
                isr->set_target_url_base(new_url);
            }
        }
    }

    return result_timeline;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
