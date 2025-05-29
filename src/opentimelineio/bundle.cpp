// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/bundle.h"
#include "opentimelineio/bundleUtils.h"
#include "opentimelineio/timeline.h"

#include <filesystem>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION { namespace bundle {

bool
to_otiod_bundle(
    Timeline const*            timeline,
    std::string const&         file_name,
    BundleMediaReferencePolicy media_reference_policy,
    ErrorStatus*               error_status,
    const schema_version_map*  target_family_label_spec,
    int                        indent)
{
    // Make a copy of the timeline so we can change the media references.
    SerializableObject::Retainer<Timeline> timelineCopy(
        dynamic_cast<Timeline*>(timeline->clone()));

    // Write the timeline to the bundle.
    const std::filesystem::path path = std::filesystem::u8path(file_name);
    bool                        r    = timelineCopy->to_json_file(
        (path / "content.otio").u8string(),
        error_status,
        target_family_label_spec,
        indent);
    if (r)
    {
    }
    return r;
}

} // namespace bundle
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
