// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief A reference to an image sequence.
///
/// Image file names are composed from a target URL base, name prefix, name
/// suffix, frame number, and zero padding. For example the image file name
/// "file:///path/to/image.000100.exr":
/// * Target URL base: file:///path/to/
/// * Name prefix: "image."
/// * Name suffix: ".exr"
/// * Frame number padded to six zeroes: "000100"
class OTIO_API_TYPE ImageSequenceReference final : public MediaReference
{
public:
    /// @brief How to handle missing frames.
    enum MissingFramePolicy
    {
        error = 0,
        hold  = 1,
        black = 2
    };

    /// @brief This struct provides the ImageSequenceReference schema.
    struct Schema
    {
        static auto constexpr name   = "ImageSequenceReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    /// @brief Create a new image sequence reference.
    ///
    /// @param target_url_base The base of the URL.
    /// @param name_prefix The prefix of the file name.
    /// @param name_suffix The suffix of the file name.
    /// @param start_frame The start frame of the image sequence.
    /// @param frame_step The frame step of the image sequence.
    /// @param rate The frame rate of the image sequence.
    /// @param frame_zero_padding The number of zeroes used to pad the frame numbers.
    /// @param missing_frame_policy How to handle missing frames.
    /// @param available_range The available range of the image sequence.
    /// @param metadata The metadata for the image sequence.
    /// @param available_image_bounds The spatial bounds of the image sequence.
    ImageSequenceReference(
        std::string const&       target_url_base    = std::string(),
        std::string const&       name_prefix        = std::string(),
        std::string const&       name_suffix        = std::string(),
        int                      start_frame        = 1,
        int                      frame_step         = 1,
        double                   rate               = 1,
        int                      frame_zero_padding = 0,
        MissingFramePolicy const missing_frame_policy =
            MissingFramePolicy::error,
        std::optional<TimeRange> const& available_range = std::nullopt,
        AnyDictionary const&            metadata        = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds =
            std::nullopt);

    /// @brief Return the URL base.
    std::string target_url_base() const noexcept { return _target_url_base; }

    /// @brief Set the URL base.
    void set_target_url_base(std::string const& target_url_base)
    {
        _target_url_base = target_url_base;
    }

    /// @brief Return the file name prefix.
    std::string name_prefix() const noexcept { return _name_prefix; }

    /// @brief Set the file name prefix.
    void set_name_prefix(std::string const& target_url_base)
    {
        _name_prefix = target_url_base;
    }

    /// @brief Return the file name suffix.
    std::string name_suffix() const noexcept { return _name_suffix; }

    /// @brief Set the file name suffix.
    void set_name_suffix(std::string const& target_url_base)
    {
        _name_suffix = target_url_base;
    }

    /// @brief Return the start frame.
    int start_frame() const noexcept { return _start_frame; }

    /// @brief Set the start frame.
    void set_start_frame(int start_frame) noexcept
    {
        _start_frame = start_frame;
    }

    /// @brief Return the frame step.
    int frame_step() const noexcept { return _frame_step; }

    /// @brief Set the frame step.
    void set_frame_step(int frame_step) noexcept { _frame_step = frame_step; }

    /// @brief Return the frame rate.
    double rate() const noexcept { return _rate; }

    /// @brief Set the frame rate.
    void set_rate(double rate) noexcept { _rate = rate; }

    /// @brief Return the frame number zero padding.
    int frame_zero_padding() const noexcept { return _frame_zero_padding; }

    /// @brief Set the frame number zero padding.
    void set_frame_zero_padding(int frame_zero_padding) noexcept
    {
        _frame_zero_padding = frame_zero_padding;
    }

    /// @brief Set the missing frame policy.
    void
    set_missing_frame_policy(MissingFramePolicy missing_frame_policy) noexcept
    {
        _missing_frame_policy = missing_frame_policy;
    }

    /// @brief Return the missing frame policy.
    MissingFramePolicy missing_frame_policy() const noexcept
    {
        return _missing_frame_policy;
    }

    /// @brief Return the end frame.
    int end_frame() const;

    /// @brief Return the number of images in the sequence.
    int number_of_images_in_sequence() const;

    /// @brief Return the frame for the given time.
    int frame_for_time(
        RationalTime const& time,
        ErrorStatus*        error_status = nullptr) const;

    /// @brief Return the target URL for the given image number.
    std::string target_url_for_image_number(
        int          image_number,
        ErrorStatus* error_status = nullptr) const;

    /// @brief Return the presentation time for the given image number.
    RationalTime presentation_time_for_image_number(
        int          image_number,
        ErrorStatus* error_status = nullptr) const;

protected:
    virtual ~ImageSequenceReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string        _target_url_base;
    std::string        _name_prefix;
    std::string        _name_suffix;
    int                _start_frame;
    int                _frame_step;
    double             _rate;
    int                _frame_zero_padding;
    MissingFramePolicy _missing_frame_policy;

    RationalTime frame_duration() const noexcept;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
