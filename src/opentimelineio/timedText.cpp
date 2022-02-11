#include "opentimelineio/timedText.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {

        TimedText::TimedText(RationalTime const &in_time,
                             RationalTime const &out_time)
                : Parent() {
            set_marked_range(TimeRange::range_from_start_end_time(in_time, out_time));
        }

        TimedText::~TimedText() {}

        bool TimedText::read_from(Reader &reader) {
            return reader.read("texts", &_texts) &&
                   reader.read("style_ids", &_styleIDs) &&
                   Parent::read_from(reader);
        }

        void TimedText::write_to(Writer &writer) const {
            Parent::write_to(writer);
            writer.write("texts", _texts);
            writer.write("style_ids", _styleIDs);
        }

    }
}
