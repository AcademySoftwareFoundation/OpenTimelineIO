// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/indexStreamAddress.h"
#include "opentimelineio/streamAddress.h"
#include "opentimelineio/stringStreamAddress.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Describes a single media stream provided within a source media.
///
/// A media stream is the smallest unit of temporal media source such as a
/// single eye's video, an isolated audio channel, or a camera view within a 3D
/// scene.
/// `StreamAddress` provides a mechanism for addressing a specific stream within
/// a media container.
class OTIO_API_TYPE StreamInfo : public SerializableObjectWithMetadata
{
public:
    /// @brief Well-known strings for identifying common semantic roles of media
    /// streams. These generally map to presentation devices (e.g. a spcific
    /// speaker or one eye's view in a head-mounted display).
    ///
    /// In aural media, stereo pairs are called out distinctly from
    /// immmersive/surround channels because they are not totally
    /// interchangeable - simply presenting the left and right from a surround
    /// mix is generally not a desired experience.
    ///
    /// The surround names are inspired by ITU-R BS.2051-3 using the following
	/// modifications:
	/// - Use the US spelling consistent with current OTIO spelling.
	///	- Add "surround" prefix to group surround audio channel names
    /// - Replace the "surround" postfix with "rear"
	/// - Add "front" postfix to clarify names like "surround_left"
    /// Additional names can be added from that specification using a similar
	/// pattern if needed.
    struct Identifier
    {
        // Visual media

        /// A single video stream that contains all views, e.g. a traditional 2D video
        static char constexpr monocular[]               = "monocular";
        /// The left eye's video stream in a stereo pair.
        static char constexpr left_eye[]                = "left_eye";
        /// The right eye's video stream in a stereo pair.
        static char constexpr right_eye[]               = "right_eye";

        // Simple aural media

        /// A single monaural audio stream.
        static char constexpr monaural[]                = "monaural";
        /// The left channel of a stereo pair.
        static char constexpr stereo_left[]             = "stereo_left";
        /// The right channel of a stereo pair.
        static char constexpr stereo_right[]            = "stereo_right";

        // Immersive or surround aural media

        /// The left front surround channel (L).
        static char constexpr surround_left_front[]          = "surround_left_front";
        /// The right front surround channel (R).
        static char constexpr surround_right_front[]         = "surround_right_front";
        /// The center surround channel (C).
        static char constexpr surround_center_front[]        = "surround_center_front";
        /// The left rear surround channel (Ls).
        static char constexpr surround_left_rear[]           = "surround_left_rear";
        /// The right rear surround channel (Rs).
        static char constexpr surround_right_rear[]          = "surround_right_rear";
        /// The low frequency effects (LFE) channel.
        static char constexpr surround_low_frequency_effects[] = "surround_low_frequency_effects";
    };

    /// @brief This struct provides the StreamInfo schema.
    struct Schema
    {
        static char constexpr name[]  = "StreamInfo";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new StreamInfo.
    ///
    /// @param name A human-readable label for this stream. May be any
    ///   descriptive string, e.g. "Alice lavalier (boom backup)",
    ///   "left eye 4K".
    /// @param address The address of the stream within the media container.
    /// @param kind A string identifying the kind of stream. When applicable,
    ///   use a value `Track::Kind`.
    /// @param metadata Optional metadata dictionary.
    OTIO_API StreamInfo(
        std::string const&   name    = std::string(),
        StreamAddress* address = nullptr,
        std::string const&   kind    = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

    /// @brief The stream address.
    StreamAddress* address() const noexcept
    {
        return dynamic_retainer_cast<StreamAddress>(_address);
    }

    /// @brief Set the stream address.
    void set_address(StreamAddress* address) { _address = address; }

    /// @brief The stream kind.
    ///
    /// This describes the kind of media represented by this stream.
    /// When applicable, this should be a value from `Track::Kind`.
    std::string kind() const noexcept { return _kind; }

    /// @brief Set the stream kind.
    ///
    /// This describes the kind of media represented by this stream.
    /// When applicable, this should be a value from `Track::Kind`.
    void set_kind(std::string const& kind) { _kind = kind; }

protected:
    virtual ~StreamInfo();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    Retainer<StreamAddress> _address;
    std::string                   _kind;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
