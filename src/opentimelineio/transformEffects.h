#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief An scaling effect
class VideoScale : public Effect
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "VideoScale";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new scaling effect.
    ///
    /// @param name The name of the effect object.
    /// @param width How much to scale the width by.
    /// @param height How much to scale the height by.
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    VideoScale(
        std::string const&   name        = std::string(),
        int64_t              width       = 0,
        int64_t              height      = 0,
        AnyDictionary const& metadata    = AnyDictionary())
        : Effect(name, Schema::name, metadata)
        , _width(width)
        , _height(height)
    {}

    int64_t width() const noexcept { return _width; }
    int64_t height() const noexcept { return _height; }

    void set_width(int64_t width) noexcept { _width = width; }
    void set_height(int64_t height) noexcept { _height = height; }

protected:

    virtual ~VideoScale() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _width;  ///< The scaled width
    int64_t _height; ///< The scaled height
};

/// @brief An crop effect
class VideoCrop : public Effect
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "VideoCrop";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new crop effect.
    ///
    /// @param name The name of the effect object.
    /// @param left The amount to crop from the left.
    /// @param right The amount to crop from the right.
    /// @param top The amount to crop from the top.
    /// @param bottom The amount to crop from the bottom.
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    VideoCrop(
        std::string const&   name        = std::string(),
        int64_t              left        = 0,
        int64_t              right       = 0,
        int64_t              top         = 0,
        int64_t              bottom      = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _left(left)
        , _right(right)
        , _top(top)
        , _bottom(bottom)
    {}

    int64_t left() const noexcept { return _left; }
    int64_t right() const noexcept { return _right; }
    int64_t top() const noexcept { return _top; }
    int64_t bottom() const noexcept { return _bottom; }

    void set_left(int64_t left) noexcept { _left = left; }
    void set_right(int64_t right) noexcept { _right = right; }
    void set_top(int64_t top) noexcept { _top = top; }
    void set_bottom(int64_t bottom) noexcept { _bottom = bottom; }

protected:
    virtual ~VideoCrop() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _left;   ///< The amount to crop from the left.
    int64_t _right;  ///< The amount to crop from the right.
    int64_t _top;    ///< The amount to crop from the top.
    int64_t _bottom; ///< The amount to crop from the bottom.
};

/// @brief An position effect
class VideoPosition : public Effect
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "VideoPosition";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new position effect.
    ///
    /// @param name The name of the effect object.
    /// @param x Distance of top left corner from left edge of canvas
    /// @param y Distance of top left corner from top edge of canvas
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    VideoPosition(
        std::string const&   name        = std::string(),
        int64_t              x           = 0,
        int64_t              y           = 0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _x(x)
        , _y(y)
    {}

    int64_t x() const noexcept { return _x; }
    int64_t y() const noexcept { return _y; }

    void set_x(int64_t x) noexcept { _x = x; }
    void set_y(int64_t y) noexcept { _y = y; }

protected:
    virtual ~VideoPosition() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    int64_t _x; ///< The horizontal position.
    int64_t _y; ///< The vertical position.
};

/// @brief An rotation effect
class VideoRotate : public Effect
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "VideoRotate";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new rotation effect.
    ///
    /// @param name The name of the effect object.
    /// @param angle The amount of rotation, degrees clockwise
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    VideoRotate(
        std::string const&   name        = std::string(),
        double               angle      = 0.0,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _angle(angle)
    {}

    double angle() const noexcept { return _angle; }
    void set_angle(double angle) noexcept { _angle = angle; }

protected:
    virtual ~VideoRotate() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    double _angle; ///< The angle of rotation, degrees clockwise
};

/// @brief A flip effect
class VideoFlip : public Effect
{
public:
    struct Schema
    {
        static auto constexpr name   = "VideoFlip";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new flip effect.
    ///
    /// @param name The name of the effect object.
    /// @param flip_horizontally Whether to flip horizontally.
    /// @param flip_vertically Whether to flip vertically.
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    VideoFlip(
        std::string const&   name        = std::string(),
        bool                 flip_horizontally = false,
        bool                 flip_vertically = false,
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true)
        : Effect(name, Schema::name, metadata, enabled)
        , _flip_horizontally(flip_horizontally)
        , _flip_vertically(flip_vertically)
    {}

    bool flip_horizontally() const noexcept { return _flip_horizontally; }
    void set_flip_horizontally(bool flip_horizontally) noexcept { _flip_horizontally = flip_horizontally; }

    bool flip_vertically() const noexcept { return _flip_vertically; }
    void set_flip_vertically(bool flip_vertically) noexcept { _flip_vertically = flip_vertically; }

protected:
    virtual ~VideoFlip() = default;
    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    bool _flip_horizontally; ///< Whether to flip horizontally
    bool _flip_vertically; ///< Whether to flip vertically
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
