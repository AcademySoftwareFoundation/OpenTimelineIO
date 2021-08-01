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

            explicit TimedText(RationalTime const &in_time = RationalTime(),
                               RationalTime const &out_time = RationalTime());

            std::vector<std::string> const &texts() const {
                return _texts;
            }

            std::vector<std::string> const &styleIDs() const {
                return _texts;
            }

            void add_text(std::string const &text, std::string const &styleID = "") {
                _texts.emplace_back(text);
                _styleIDs.emplace_back(styleID);
            }

            RationalTime in_time() const {
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
            std::vector<std::string> _texts;
            std::vector<std::string> _styleIDs;
        };

    }
}
