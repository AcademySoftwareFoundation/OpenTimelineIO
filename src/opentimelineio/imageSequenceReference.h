#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class ImageSequenceReference final : public MediaReference {
public:
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
                      RationalTime const &frame_duration = RationalTime(1, 24),
                      int image_number_zero_padding = 0,
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

    RationalTime const& frame_duration() const {
        return _frame_duration;
    }

    void set_frame_duration(RationalTime const& frame_duration) {
        _frame_duration = frame_duration;
    }

    int image_number_zero_padding() const {
        return _image_number_zero_padding;
    }

    void set_image_number_zero_padding(int const image_number_zero_padding) {
        _image_number_zero_padding = image_number_zero_padding;
    }

    int number_of_images_in_sequence() const;

    std::string
    target_url_for_image_number(int const image_number, ErrorStatus* error_status) const;

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
    RationalTime _frame_duration;
    int _image_number_zero_padding;
};

} }