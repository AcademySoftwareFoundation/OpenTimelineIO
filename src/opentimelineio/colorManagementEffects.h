#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief A brightness effect
class VideoBrightness : public Effect
{
public:
    struct Schema {
        static auto constexpr name   = "VideoBrightness";
        static int constexpr version = 1;
    };
    using Parent = Effect;

    VideoBrightness(
        std::string const&   name        = std::string(),
        int64_t              brightness  = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _brightness(brightness)
    {}

    int64_t brightness() const noexcept { return _brightness; }
    void set_brightness(int64_t brightness) noexcept { _brightness = brightness; }

protected:
    virtual ~VideoBrightness() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _brightness;
};

/// @brief A contrast effect
class VideoContrast : public Effect
{
public:
    struct Schema {
        static auto constexpr name   = "VideoContrast";
        static int constexpr version = 1;
    };
    using Parent = Effect;

    VideoContrast(
        std::string const&   name        = std::string(),
        int64_t              contrast    = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _contrast(contrast)
    {}

    int64_t contrast() const noexcept { return _contrast; }
    void set_contrast(int64_t contrast) noexcept { _contrast = contrast; }

protected:
    virtual ~VideoContrast() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _contrast;
};

/// @brief A saturation effect
class VideoSaturation : public Effect
{
public:
    struct Schema {
        static auto constexpr name   = "VideoSaturation";
        static int constexpr version = 1;
    };
    using Parent = Effect;

    VideoSaturation(
        std::string const&   name        = std::string(),
        int64_t              saturation  = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _saturation(saturation)
    {}

    int64_t saturation() const noexcept { return _saturation; }
    void set_saturation(int64_t saturation) noexcept { _saturation = saturation; }

protected:
    virtual ~VideoSaturation() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _saturation;
};

/// @brief A lightness effect
class VideoLightness : public Effect
{
public:
    struct Schema {
        static auto constexpr name   = "VideoLightness";
        static int constexpr version = 1;
    };
    using Parent = Effect;

    VideoLightness(
        std::string const&   name        = std::string(),
        int64_t              lightness   = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _lightness(lightness)
    {}

    int64_t lightness() const noexcept { return _lightness; }
    void set_lightness(int64_t lightness) noexcept { _lightness = lightness; }

protected:
    virtual ~VideoLightness() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _lightness;
};

/// @brief A color temperature effect
class VideoColorTemperature : public Effect
{
public:
    struct Schema {
        static auto constexpr name   = "VideoColorTemperature";
        static int constexpr version = 1;
    };
    using Parent = Effect;

    VideoColorTemperature(
        std::string const&   name        = std::string(),
        int64_t              temperature = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _temperature(temperature)
    {}

    int64_t temperature() const noexcept { return _temperature; }
    void set_temperature(int64_t temperature) noexcept { _temperature = temperature; }

protected:
    virtual ~VideoColorTemperature() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _temperature;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
