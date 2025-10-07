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
        double               brightness  = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _brightness(brightness)
    {}

    double brightness() const noexcept { return _brightness; }
    void set_brightness(double brightness) noexcept { _brightness = brightness; }

protected:
    virtual ~VideoBrightness() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    double _brightness;
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
        double               contrast    = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _contrast(contrast)
    {}

    double contrast() const noexcept { return _contrast; }
    void set_contrast(double contrast) noexcept { _contrast = contrast; }

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
        double               saturation  = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _saturation(saturation)
    {}

    double saturation() const noexcept { return _saturation; }
    void set_saturation(double saturation) noexcept { _saturation = saturation; }

protected:
    virtual ~VideoSaturation() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    double _saturation;
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
        double               lightness   = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _lightness(lightness)
    {}

    double lightness() const noexcept { return _lightness; }
    void set_lightness(double lightness) noexcept { _lightness = lightness; }

protected:
    virtual ~VideoLightness() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    double _lightness;
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
        double               temperature = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _temperature(temperature)
    {}

    double temperature() const noexcept { return _temperature; }
    void set_temperature(double temperature) noexcept { _temperature = temperature; }

protected:
    virtual ~VideoColorTemperature() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    double _temperature;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
