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
                      int start_frame = 1,
                      int frame_step = 1,
                      double const rate = 1,
                      int frame_zero_padding = 0,
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

    int start_frame() const {
        return _start_frame;
    }

    void set_start_frame(int const start_frame) {
        _start_frame = start_frame;
    }

    int frame_step() const {
        return _frame_step;
    }

    void set_frame_step(int const frame_step) {
        _frame_step = frame_step;
    }

    double const& rate() const {
        return _rate;
    }

    void set_rate(double const rate) {
        _rate = rate;
    }

    int frame_zero_padding() const {
        return _frame_zero_padding;
    }

    void set_frame_zero_padding(int const frame_zero_padding) {
        _frame_zero_padding = frame_zero_padding;
    }

    void set_missing_frame_policy(MissingFramePolicy const missing_frame_policy) {
        _missing_frame_policy = missing_frame_policy;
    }

    MissingFramePolicy missing_frame_policy() const {
        return _missing_frame_policy;
    }

    int end_frame() const;
    int number_of_images_in_sequence() const;
    int frame_for_time(RationalTime const time, ErrorStatus* error_status) const;

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
    int _start_frame;
    int _frame_step;
    double _rate;
    int _frame_zero_padding;
    MissingFramePolicy _missing_frame_policy;
    
    RationalTime frame_duration() const;
};

} }
