#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Sets the audio volume
class AudioVolume : public Effect
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "AudioVolume";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new volume effect.
    ///
    /// @param name The name of the effect object.
    /// @param gain Gain value
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    AudioVolume(
        std::string const& name       = std::string(),
        double gain                   = 1.0,
        AnyDictionary const& metadata = AnyDictionary())
        : Effect(name, Schema::name, metadata)
        , _gain(gain)
    {}

    double gain() const noexcept { return _gain; }
    void set_gain(double gain) noexcept { _gain = gain; }

protected:

    virtual ~AudioVolume() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    double _gain; ///< the gain
};

/// @brief Describes an audio fade effect
class AudioFade : public Effect
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "AudioFade";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new audio fade effect.
    ///
    /// @param name The name of the effect object.
    /// @param fade_in Whether this is a fade-in (true) or fade-out (false).
    /// @param start_time The start time of the fade in seconds.
    /// @param duration Duration of the fade in seconds.
    /// @param metadata The metadata for the effect.
    AudioFade(
        std::string const&   name        = std::string(),
        bool                 fade_in     = true,
        double               start_time  = 0.0,
        double               duration    = 0.0,
        AnyDictionary const& metadata    = AnyDictionary())
        : Effect(name, Schema::name, metadata)
        , _fade_in(fade_in)
        , _start_time(start_time)
        , _duration(duration)
    {}

    bool fade_in() const noexcept { return _fade_in; }
    void set_fade_in(bool fade_in) noexcept { _fade_in = fade_in; }

    double start_time() const noexcept { return _start_time; }
    void set_start_time(double start_time) noexcept { _start_time = start_time; }

    double duration() const noexcept { return _duration; }
    void set_duration(double duration) noexcept { _duration = duration; }

protected:

    virtual ~AudioFade() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    bool _fade_in;         ///< true for fade-in, false for fade-out
    double _start_time;    ///< start time of the fade in seconds
    double _duration;      ///< duration of the fade in seconds
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
