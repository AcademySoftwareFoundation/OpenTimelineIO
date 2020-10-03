#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/marker.h"
#include "opentimelineio/timedTextStyle.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {

        class TimedText : public Marker {
        public:
            struct Schema {
                static auto constexpr name = "TimedText";
                static int constexpr version = 1;
            };

            using Parent = Marker;

            TimedText(std::string const &text = std::string(),
                      RationalTime const &in_time = RationalTime(),
                      RationalTime const &out_time = RationalTime(),
                      TimedTextStyle *style = new TimedTextStyle());

            std::string const &text() const {
                return _text;
            }

            void set_text(std::string const &text) {
                _text = text;
            }

            TimedTextStyle* style() const {
                return _style.value;
            }

            void set_style(TimedTextStyle *style) {
                _style = style;
            }

            RationalTime const in_time() const {
                return marked_range().start_time();
            }

            RationalTime out_time() const {
                return marked_range().end_time_exclusive();
            }

        protected:
            ~TimedText();

            virtual bool read_from(Reader &);

            virtual void write_to(Writer &) const;

        private:
            std::string _text;
            Retainer <TimedTextStyle> _style;
        };

    }
}
