// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

#include <map>
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief An effect that mixes audio streams using a coefficient matrix.
///
/// The matrix maps output stream names to a dictionary of input stream names
/// and their mix coefficients.  Output keys SHOULD use values from
/// `StreamInfo::Identifier` (e.g. `left`, `right`) where applicable; they
/// correspond to the keys that will appear in the downstream available_streams
/// map after mixing.  Input keys identify the source streams and SHOULD match
/// the corresponding keys in the upstream `MediaReference::available_streams`.
///
/// Example — matrix to downmix 5.1 surround to Lo/Ro stereo :
/// @code{.json}
///   {
///     "left":  {
///       "left": 1.0,
///       "surround_center_front": 0.707,
///       "surround_left_rear": 0.707
///     },
///     "right": {
///       "right": 1.0,
///       "surround_center_front": 0.707,
///       "surround_right_rear": 0.707
///     }
///   }
/// @endcode
class OTIO_API_TYPE AudioMixMatrix : public Effect
{
public:
    /// @brief This struct provides the AudioMixMatrix schema.
    struct Schema
    {
        static char constexpr name[]  = "AudioMixMatrix";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    using MixMatrix = std::map<std::string, std::map<std::string, double>>;

    // @brief Create a new audio mix matrix effect.
    ///
    /// @param matrix Mixing matrix structured as:
    ///    ```
    ///    {output_name: {source_name: contribution_coefficient}}
    ///    ```
    /// @param metadata Any additional metadata to persist.
    OTIO_API AudioMixMatrix(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        MixMatrix const&     matrix      = MixMatrix(),
        AnyDictionary const& metadata    = AnyDictionary());

    /// @brief Return a const reference to the mix matrix.
    OTIO_API MixMatrix const& matrix() const noexcept { return _matrix; }

    /// @brief Set the mix matrix.
    OTIO_API void set_matrix(MixMatrix const& matrix) { _matrix = matrix; }

protected:
    virtual ~AudioMixMatrix();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    MixMatrix _matrix;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
