#include "opentimelineio/timedText.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {

        TimedText::TimedText(std::string const &text,
                             RationalTime const &in_time,
                             RationalTime const &out_time,
                             TimedTextStyle *style)
                : Parent(),
                  _text(text),
                  _style(style) {
            set_marked_range(TimeRange::range_from_start_end_time(in_time, out_time));
        }

        TimedText::~TimedText() {}

        bool TimedText::read_from(Reader &reader) {
            return reader.read("text", &_text) &&
                   reader.read("style", &_style) &&
                   Parent::read_from(reader);
        }

        void TimedText::write_to(Writer &writer) const {
            Parent::write_to(writer);
            writer.write("text", _text);
            writer.write("style", _style);
        }

    }
}
