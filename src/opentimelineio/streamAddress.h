// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Base class for addressing a specific media stream within a media
/// reference.
/// @see `StreamInfo` for more detail on media streams.
/// Specific stream address subclasses provide different mechansims for
/// identifying a stream within a container format. The semantics of which
/// StreamAddress subclass to use and how to interpret it are dependent on the
/// container format the media is accessed within.
class OTIO_API_TYPE StreamAddress : public SerializableObject
{
public:
    /// @brief This struct provides the StreamAddress schema.
    struct Schema
    {
        static char constexpr name[]  = "StreamAddress";
        static int constexpr version = 1;
    };

    using Parent = SerializableObject;

    OTIO_API StreamAddress();

protected:
    virtual ~StreamAddress();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
