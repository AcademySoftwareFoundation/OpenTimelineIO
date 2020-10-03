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

            Subtitles(float extent_x = 0.f,
                      float extent_y = 0.f,
                      float padding_x = 0.f,
                      float padding_y = 0.f,
                      std::string background_color = std::string(),
                      float background_opacity = 0.f,
                      DisplayAlignment display_alignment = DisplayAlignment::after,
                      std::vector<TimedText *> timed_texts = std::vector<TimedText *>());

            virtual TimeRange available_range(ErrorStatus *error_status) const;

            float const extent_x() const {
                return _extent_x;
            }

            void set_extent_x(float const extent_x) {
                _extent_x = extent_x;
            }

            float const extent_y() const {
                return _extent_y;
            }

            void set_extent_y(float const extent_y) {
                _extent_y = extent_y;
            }

            float const padding_x() const {
                return _padding_x;
            }

            void set_padding_x(float const padding_x) {
                _padding_x = padding_x;
            }

            float const padding_y() const {
                return _padding_y;
            }

            void set_padding_y(float const padding_y) {
                _padding_y = padding_y;
            }

            std::string const &background_color() const {
                return _background_color;
            }

            void set_background_color(std::string const &background_color) {
                _background_color = background_color;
            }

            float const background_opacity() const {
                return _background_opacity;
            }

            void set_background_opacity(float const background_opacity) {
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
            float _extent_x;
            float _extent_y;
            float _padding_x;
            float _padding_y;
            std::string _background_color;
            float _background_opacity;
            DisplayAlignment _display_alignment;
            std::vector<Retainer < TimedText>> _timed_texts;
        };

    }
}
