#include "opentimelineio/imageSequenceReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

ImageSequenceReference::ImageSequenceReference(std::string const& target_url_base,
                      std::string const& name_prefix,
                      std::string const& name_suffix,
                      int start_frame,
                      int frame_step,
                      double const rate,
                      int frame_zero_padding,
                      MissingFramePolicy const missing_frame_policy,
                      optional<TimeRange> const& available_range,
                      AnyDictionary const& metadata)
    : Parent(std::string(), available_range, metadata),
    _target_url_base(target_url_base),
    _name_prefix(name_prefix),
    _name_suffix(name_suffix),
    _start_frame {start_frame},
    _frame_step {frame_step},
    _rate {rate},
    _frame_zero_padding {frame_zero_padding},
    _missing_frame_policy {missing_frame_policy} {
    }

    ImageSequenceReference::~ImageSequenceReference() {
    }

    RationalTime
    ImageSequenceReference::frame_duration() const {
        return RationalTime((double)_frame_step, _rate);
    }

    int ImageSequenceReference::end_frame() const {
        if (!this->available_range().has_value()) {
            return _start_frame;
        }

        int num_frames = this->available_range().value().duration().to_frames(_rate);

        // Subtract 1 for inclusive frame ranges
        return (_start_frame + num_frames - 1);
    }

    int ImageSequenceReference::number_of_images_in_sequence() const {
        if (!this->available_range().has_value()) {
            return 0;
        }

        double playback_rate = (_rate / (double)_frame_step);
        int num_frames = this->available_range().value().duration().to_frames(playback_rate);
        return num_frames;
    }

    int ImageSequenceReference::frame_for_time(RationalTime const time, ErrorStatus* error_status) const {
        if (!this->available_range().has_value() || !this->available_range().value().contains(time)) {
            *error_status = ErrorStatus(ErrorStatus::INVALID_TIME_RANGE);
            return 0;
        }

        RationalTime start = this->available_range().value().start_time();
        RationalTime duration_from_start = (time - start);
        int frame_offset = duration_from_start.to_frames(_rate);

        *error_status = ErrorStatus(ErrorStatus::OK);

        return (_start_frame + frame_offset);
    }

    std::string
    ImageSequenceReference::target_url_for_image_number(int const image_number, ErrorStatus* error_status) const {
        if (_rate == 0) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX, "Zero rate sequence has no frames.");
            return std::string();
        }
        else if (!this->available_range().has_value() || this->available_range().value().duration().value() == 0) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX, "Zero duration sequences has no frames.");
            return std::string();
        }
        else if (image_number >= this->number_of_images_in_sequence()) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX);
            return std::string();
        }
        const int file_image_num = _start_frame + (image_number * _frame_step);
        const bool is_negative = (file_image_num < 0);

        std::string image_num_string = std::to_string(abs(file_image_num));

        std::string zero_pad = std::string();
        if (image_num_string.length() <  _frame_zero_padding) {
            zero_pad = std::string(_frame_zero_padding - image_num_string.length(), '0');
        }

        std::string sign = std::string();
        if (is_negative) {
            sign = "-";
        }

        // If the base does not include a trailing slash, add it
        std::string path_sep = std::string();
        if (_target_url_base.compare(_target_url_base.length() - 1, 1, "/") != 0) {
            path_sep = "/";
        }

        std::string out_string = _target_url_base + path_sep + _name_prefix + sign + zero_pad + image_num_string + _name_suffix;
        *error_status = ErrorStatus(ErrorStatus::OK);
        return out_string;
    }

    RationalTime
    ImageSequenceReference::presentation_time_for_image_number(int const image_number, ErrorStatus* error_status) const {
        if (image_number >= this->number_of_images_in_sequence()) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX);
            return RationalTime();
        }

        auto first_frame_time = this->available_range().value().start_time();
        auto time_multiplier = TimeTransform(first_frame_time, image_number, -1);
        return time_multiplier.applied_to(frame_duration());
    }

    bool ImageSequenceReference::read_from(Reader& reader) {
        auto result = reader.read("target_url_base", &_target_url_base) &&
            reader.read("name_prefix", &_name_prefix) &&
            reader.read("name_suffix", &_name_suffix) &&
            reader.read("start_frame", &_start_frame) &&
            reader.read("frame_step", &_frame_step) &&
            reader.read("rate", &_rate) &&
            reader.read("frame_zero_padding", &_frame_zero_padding);

        std::string missing_frame_policy_value;
        result && reader.read("missing_frame_policy", &missing_frame_policy_value);
        if (!result) {
            return result;
        }

        if (missing_frame_policy_value == "error") {
            _missing_frame_policy = MissingFramePolicy::error;
        }
        else if (missing_frame_policy_value == "black") {
            _missing_frame_policy = MissingFramePolicy::black;
        }
        else if (missing_frame_policy_value == "hold") {
            _missing_frame_policy = MissingFramePolicy::hold;
        }
        else {
            // Unrecognized value
            ErrorStatus error_status = ErrorStatus(ErrorStatus::JSON_PARSE_ERROR,
                       "Unknown missing_frame_policy: " + missing_frame_policy_value);
            reader.error(error_status);
            return false;
        }

        return result && Parent::read_from(reader);
    }

    void ImageSequenceReference::write_to(Writer& writer) const {
        Parent::write_to(writer);
        writer.write("target_url_base", _target_url_base);
        writer.write("name_prefix", _name_prefix);
        writer.write("name_suffix", _name_suffix);
        writer.write("start_frame", _start_frame);
        writer.write("frame_step", _frame_step);
        writer.write("rate", _rate);
        writer.write("frame_zero_padding", _frame_zero_padding);

        std::string missing_frame_policy_value;
        switch (_missing_frame_policy)
        {
        case MissingFramePolicy::error:
            missing_frame_policy_value = "error";
            break;
        case MissingFramePolicy::black:
            missing_frame_policy_value = "black";
            break;
        case MissingFramePolicy::hold:
            missing_frame_policy_value = "hold";
            break;
        }
        writer.write("missing_frame_policy", missing_frame_policy_value);
    }
} }
