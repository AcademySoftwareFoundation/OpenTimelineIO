// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/streamAddress.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Addresses a stream by string identifier (e.g. codec name or channel label).
class OTIO_API_TYPE StringStreamAddress : public StreamAddress
{
public:
    /// @brief This struct provides the StringStreamAddress schema.
    struct Schema
    {
        static char constexpr name[]  = "StringStreamAddress";
        static int constexpr version = 1;
    };

    using Parent = StreamAddress;

    OTIO_API explicit StringStreamAddress(std::string const& address = std::string());

    /// @brief Return the stream address string.
    std::string address() const noexcept { return _address; }

    /// @brief Set the stream address string.
    void set_address(std::string const& address) { _address = address; }

protected:
    virtual ~StringStreamAddress();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _address;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
