// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

#include <vector>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief An effect that selects specific named output streams from an item.
///
/// Use this to select a stereo view, specific audio channels, etc.
/// The clip will expose these streams out with the same naming.
class OTIO_API_TYPE StreamSelector : public Effect
{
public:
    /// @brief This struct provides the StreamSelector schema.
    struct Schema
    {
        static char constexpr name[]  = "StreamSelector";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new StreamSelector.
    ///
    /// @param name The name of the effect object.
    /// @param effect_name The name of the effect.
    /// @param output_streams The list of stream identifiers to select.
    /// @param metadata The metadata for the effect.
    OTIO_API StreamSelector(
        std::string const&              name           = std::string(),
        std::string const&              effect_name    = std::string(),
        std::vector<std::string> const& output_streams = std::vector<std::string>(),
        AnyDictionary const&            metadata       = AnyDictionary());

    /// @brief Return the list of output stream identifiers.
    std::vector<std::string> const& output_streams() const noexcept
    {
        return _output_streams;
    }

    /// @brief Set the list of output stream identifiers.
    void set_output_streams(std::vector<std::string> const& output_streams)
    {
        _output_streams = output_streams;
    }

protected:
    virtual ~StreamSelector();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::vector<std::string> _output_streams;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
