#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/item.h"
#include "opentimelineio/timedText.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {
        class Subtitles : public Item {
        public:
            enum DisplayAlignment {
                before = 0,
                after = 1,
                center = 2,
                justify = 3
            };

            struct Schema {
                static auto constexpr name = "Subtitles";
                static int constexpr version = 1;
            };

            using Parent = Item;

            Subtitles(double extent_x = 0.f,
                      double extent_y = 0.f,
                      double padding_x = 0.f,
                      double padding_y = 0.f,
                      std::string background_color = std::string(),
                      double background_opacity = 0.f,
                      DisplayAlignment display_alignment = DisplayAlignment::after,
                      std::vector<TimedText *> timed_texts = std::vector<TimedText *>());

            virtual TimeRange available_range(ErrorStatus *error_status) const;

            double const extent_x() const {
                return _extent_x;
            }

            void set_extent_x(double const extent_x) {
                _extent_x = extent_x;
            }

            double const extent_y() const {
                return _extent_y;
            }

            void set_extent_y(double const extent_y) {
                _extent_y = extent_y;
            }

            double const padding_x() const {
                return _padding_x;
            }

            void set_padding_x(double const padding_x) {
                _padding_x = padding_x;
            }

            double const padding_y() const {
                return _padding_y;
            }

            void set_padding_y(double const padding_y) {
                _padding_y = padding_y;
            }

            std::string const &background_color() const {
                return _background_color;
            }

            void set_background_color(std::string const &background_color) {
                _background_color = background_color;
            }

            double const background_opacity() const {
                return _background_opacity;
            }

            void set_background_opacity(double const background_opacity) {
                _background_opacity = background_opacity;
            }

            DisplayAlignment const display_alignment() const {
                return _display_alignment;
            }

            void set_display_alignment(DisplayAlignment const display_alignment) {
                _display_alignment = display_alignment;
            }

            std::vector<Retainer<TimedText>>& timed_texts() {
                return _timed_texts;
            }

            std::vector<Retainer<TimedText>> const& timed_texts() const {
                return _timed_texts;
            }

        protected:
            ~Subtitles();

            virtual bool read_from(Reader &);

            virtual void write_to(Writer &) const;

        private:
            double _extent_x;
            double _extent_y;
            double _padding_x;
            double _padding_y;
            std::string _background_color;
            double _background_opacity;
            DisplayAlignment _display_alignment;
            std::vector<Retainer < TimedText>> _timed_texts;
        };

    }
}
