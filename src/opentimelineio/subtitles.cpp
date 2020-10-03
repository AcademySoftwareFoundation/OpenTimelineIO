#include "opentimelineio/subtitles.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {

        Subtitles::Subtitles(double extent_x,
                             double extent_y,
                             double padding_x,
                             double padding_y,
                             std::string background_color,
                             double background_opacity,
                             DisplayAlignment display_alignment,
                             std::vector<TimedText *> timed_texts)
                : Parent(),
                  _extent_x(extent_x),
                  _extent_y(extent_y),
                  _padding_x(padding_x),
                  _padding_y(padding_y),
                  _background_color(background_color),
                  _background_opacity(background_opacity),
                  _display_alignment(display_alignment),
                  _timed_texts(timed_texts.begin(), timed_texts.end()) {
        }

        Subtitles::~Subtitles() noexcept {}

        TimeRange Subtitles::available_range(ErrorStatus *) const {
            TimeRange timeRange;
            for (auto timed_text : _timed_texts) {
                timeRange = timeRange.extended_by(timed_text.value->marked_range());
            }
            return timeRange;
        }

        bool Subtitles::read_from(Reader &reader) {
            auto result = reader.read("extent_x", &_extent_x) &&
                          reader.read("extent_y", &_extent_y) &&
                          reader.read("padding_x", &_padding_x) &&
                          reader.read("padding_y", &_padding_y) &&
                          reader.read("background_color", &_background_color) &&
                          reader.read("background_opacity", &_background_opacity) &&
                          reader.read("timed_texts", &_timed_texts);
            std::string display_alignment_value;
            result = result && reader.read("display_alignment", &display_alignment_value);
            if (!result) {
                return result;
            }

            if (display_alignment_value == "before") {
                _display_alignment = DisplayAlignment::before;
            } else if (display_alignment_value == "after") {
                _display_alignment = DisplayAlignment::after;
            } else if (display_alignment_value == "center") {
                _display_alignment = DisplayAlignment::justify;
            } else if (display_alignment_value == "justify") {
                _display_alignment = DisplayAlignment::justify;
            } else {
                // Unrecognized value
                ErrorStatus error_status = ErrorStatus(ErrorStatus::JSON_PARSE_ERROR,
                                                       "Unknown display_alignment: " + display_alignment_value);
                reader.error(error_status);
                return false;
            }

            return Parent::read_from(reader);
        }

        void Subtitles::write_to(Writer &writer) const {
            Parent::write_to(writer);
            writer.write("extent_x", _extent_x);
            writer.write("extent_y", _extent_y);
            writer.write("padding_x", _padding_x);
            writer.write("padding_y", _padding_y);
            writer.write("background_color", _background_color);
            writer.write("background_opacity", _background_opacity);
            writer.write("timed_texts", _timed_texts);

            std::string display_alignment_value;
            switch (_display_alignment) {
                case DisplayAlignment::before:
                    display_alignment_value = "before";
                    break;
                case DisplayAlignment::after:
                    display_alignment_value = "after";
                    break;
                case DisplayAlignment::center:
                    display_alignment_value = "center";
                    break;
                case DisplayAlignment::justify:
                    display_alignment_value = "justify";
                    break;
            }
            writer.write("display_alignment", display_alignment_value);
        }

    }
}
