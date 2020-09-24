#include "opentimelineio/timedTextStyle.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {

        TimedTextStyle::TimedTextStyle(const std::string &style_id,
                                       std::string text_alignment,
                                       std::string text_color,
                                       float text_size,
                                       bool text_bold,
                                       bool text_italics,
                                       bool text_underline,
                                       std::string font_family)
                : Parent(),
                  _style_id(style_id),
                  _text_alignment(text_alignment),
                  _text_color(text_color),
                  _text_size(text_size),
                  _text_bold(text_bold),
                  _text_italics(text_italics),
                  _text_underline(text_underline),
                  _font_family(font_family) {
        }

        TimedTextStyle::~TimedTextStyle() {}

        bool TimedTextStyle::read_from(Reader &reader) {
            return reader.read("style_id", &_style_id) &&
                   reader.read("text_alignment", &_text_alignment) &&
                   reader.read("text_color", &_text_color) &&
                   reader.read("text_size", &_text_size) &&
                   reader.read("text_bold", &_text_bold) &&
                   reader.read("text_italics", &_text_italics) &&
                   reader.read("text_underline", &_text_underline) &&
                   reader.read("font_family", &_font_family) &&
                   Parent::read_from(reader);
        }

        void TimedTextStyle::write_to(Writer &writer) const {
            Parent::write_to(writer);
            writer.write("style_id", _style_id);
            writer.write("text_alignment", _text_alignment);
            writer.write("text_color", _text_color);
            writer.write("text_size", _text_size);
            writer.write("text_bold", _text_bold);
            writer.write("text_italics", _text_italics);
            writer.write("text_underline", _text_underline);
            writer.write("font_family", _font_family);
        }

    }
}
