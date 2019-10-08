#include "opentimelineio/imageSequenceReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

ImageSequenceReference::ImageSequenceReference(std::string const& target_url_base,
                      std::string const& name_prefix,
                      std::string const& name_suffix,
                      int start_value,
                      int value_step,
                      RationalTime const& frame_duration,
                      int image_number_zero_padding,
                      optional<TimeRange> const& available_range,
                      AnyDictionary const& metadata)
    : Parent(std::string(), available_range, metadata),
    _target_url_base(target_url_base),
    _name_prefix(name_prefix),
    _name_suffix(name_suffix),
    _start_value {start_value},
    _value_step {value_step},
    _frame_duration {frame_duration},
    _image_number_zero_padding {image_number_zero_padding} {
    }

    ImageSequenceReference::~ImageSequenceReference() {
    }

    int ImageSequenceReference::number_of_images_in_sequence() const {
        if (!this->available_range().has_value()) {
            return 0;
        }
        
        RationalTime frame_rate = RationalTime(_frame_duration.rate(), _frame_duration.value());
        int num_frames = this->available_range().value().duration().to_frames(frame_rate.to_seconds());
        return num_frames;
    } 

    std::string
    ImageSequenceReference::target_url_for_image_number(int const image_number, ErrorStatus* error_status) const {
        if (image_number >= this->number_of_images_in_sequence()) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX);
            return std::string();
        }
        const int file_image_num = _start_value + (image_number * _value_step);
        std::string image_num_string = std::to_string(file_image_num);
        std::string zero_pad = std::string();
        if (image_num_string.length() <  _image_number_zero_padding) {
            zero_pad = std::string(_image_number_zero_padding - image_num_string.length(), '0');
        }

        std::string out_string = _target_url_base + _name_prefix + zero_pad + image_num_string + _name_suffix;
        *error_status = ErrorStatus(ErrorStatus::OK);
        return out_string;
    }

    bool ImageSequenceReference::read_from(Reader& reader) {
        return reader.read("target_url_base", &_target_url_base) &&
                reader.read("name_prefix", &_name_prefix) &&
                reader.read("name_suffix", &_name_suffix) &&
                reader.read("start_value", &_start_value) &&
                reader.read("value_step", &_value_step) &&
                reader.read("frame_duration", &_frame_duration) &&
                reader.read("image_number_zero_padding", &_image_number_zero_padding) &&
                Parent::read_from(reader);
    }

    void ImageSequenceReference::write_to(Writer& writer) const {
        Parent::write_to(writer);
        writer.write("target_url_base", _target_url_base);
        writer.write("name_prefix", _name_prefix);
        writer.write("name_suffix", _name_suffix);
        writer.write("start_value", _start_value);
        writer.write("value_step", _value_step);
        writer.write("frame_duration", _frame_duration);
        writer.write("image_number_zero_padding", _image_number_zero_padding);
}
} }