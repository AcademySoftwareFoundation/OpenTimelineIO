#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class ImageSequenceReference final : public MediaReference {
public:
    enum MissingFramePolicy {
        error = 0,
        hold = 1,
        black = 2
    };

    struct Schema {
        static auto constexpr name = "ImageSequenceReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    ImageSequenceReference(std::string const& target_url_base = std::string(),
                      std::string const& name_prefix = std::string(),
                      std::string const& name_suffix = std::string(),
                      int start_value = 1,
                      int value_step = 1,
                      double const rate = 1,
                      int image_number_zero_padding = 0,
                      MissingFramePolicy const missing_frame_policy = MissingFramePolicy::error,
                      optional<TimeRange> const& available_range = nullopt,
                      AnyDictionary const& metadata = AnyDictionary());
        
    std::string const& target_url_base() const {
        return _target_url_base;
    }
    
    void set_target_url_base(std::string const& target_url_base) {
        _target_url_base = target_url_base;
    }
        
    std::string const& name_prefix() const {
        return _name_prefix;
    }
    
    void set_name_prefix(std::string const& target_url_base) {
        _name_prefix = target_url_base;
    }

    std::string const& name_suffix() const {
        return _name_suffix;
    }
    
    void set_name_suffix(std::string const& target_url_base) {
        _name_suffix = target_url_base;
    }

    long start_value() const {
        return _start_value;
    }

    void set_start_value(long const start_value) {
        _start_value = start_value;
    }

    long value_step() const {
        return _value_step;
    }

    void set_value_step(long const value_step) {
        _value_step = value_step;
    }

    double const& rate() const {
        return _rate;
    }

    void set_rate(double const rate) {
        _rate = rate;
    }

    int image_number_zero_padding() const {
        return _image_number_zero_padding;
    }

    void set_image_number_zero_padding(int const image_number_zero_padding) {
        _image_number_zero_padding = image_number_zero_padding;
    }

    void set_missing_frame_policy(MissingFramePolicy const missing_frame_policy) {
        _missing_frame_policy = missing_frame_policy;
    }

    MissingFramePolicy missing_frame_policy() const {
        return _missing_frame_policy;
    }

    int number_of_images_in_sequence() const;

    std::string
    target_url_for_image_number(int const image_number, ErrorStatus* error_status) const;

    RationalTime
    presentation_time_for_image_number(int const image_number, ErrorStatus* error_status) const;

protected:
    virtual ~ImageSequenceReference();
 
    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _target_url_base;
    std::string _name_prefix;
    std::string _name_suffix;
    int _start_value;
    int _value_step;
    double _rate;
    int _image_number_zero_padding;
    MissingFramePolicy _missing_frame_policy;
    
    RationalTime frame_duration() const;
};

} }