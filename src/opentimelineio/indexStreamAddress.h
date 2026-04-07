// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/streamAddress.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Addresses a stream by integer index (e.g. a channel index in WAV).
class OTIO_API_TYPE IndexStreamAddress : public StreamAddress
{
public:
    /// @brief This struct provides the IndexStreamAddress schema.
    struct Schema
    {
        static char constexpr name[]  = "IndexStreamAddress";
        static int constexpr version = 1;
    };

    using Parent = StreamAddress;

    OTIO_API explicit IndexStreamAddress(int64_t index = 0);

    /// @brief Return the stream index.
    OTIO_API int64_t index() const noexcept { return _index; }

    /// @brief Set the stream index.
    OTIO_API void set_index(int64_t index) noexcept { _index = index; }

protected:
    virtual ~IndexStreamAddress();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    int64_t _index;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
