#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/marker.h"

namespace opentimelineio {
    namespace OPENTIMELINEIO_VERSION {

        class TimedTextStyle : public SerializableObject {
        public:
            struct TextAlignment {
                static auto constexpr left = "LEFT";
                static auto constexpr top = "TOP";
                static auto constexpr right = "RIGHT";
                static auto constexpr bottom = "BOTTOM";
                static auto constexpr center = "CENTER";
            };

            struct Schema {
                static auto constexpr name = "TimedTextStyle";
                static int constexpr version = 1;
            };

            using Parent = SerializableObject;

            TimedTextStyle(std::string const &style_id = std::string(),
                           std::string text_alignment = TextAlignment::bottom,
                           std::string text_color = Marker::Color::black,
                           double text_size = 10,
                           bool text_bold = false,
                           bool text_italics = false,
                           bool text_underline = false,
                           std::string font_family = std::string());

            std::string const &style_id() const {
                return _style_id;
            }

            void set_style_id(std::string const &style_id) {
                _style_id = style_id;
            }

            std::string const &text_alignment() const {
                return _text_alignment;
            }

            void set_text_alignment(std::string const &text_alignment) {
                _text_alignment = text_alignment;
            }

            std::string const &text_color() const {
                return _text_color;
            }

            void set_text_color(std::string const &text_color) {
                _text_color = text_color;
            }

            double const text_size() const {
                return _text_size;
            }

            void set_text_size(double const text_size) {
                _text_size = text_size;
            }

            bool const is_text_bold() const {
                return _text_bold;
            }

            void set_text_bold(bool const text_bold) {
                _text_bold = text_bold;
            }

            bool const is_text_italicized() const {
                return _text_italics;
            }

            void set_text_italicized(bool const text_italics) {
                _text_italics = text_italics;
            }

            bool const is_text_underlined() const {
                return _text_underline;
            }

            void set_text_underlined(bool const text_underline) {
                _text_underline = text_underline;
            }

            std::string const &font_family() const {
                return _font_family;
            }

            void set_font_family(std::string const &font_family) {
                _font_family = font_family;
            }

        protected:
            ~TimedTextStyle();

            virtual bool read_from(Reader &);

            virtual void write_to(Writer &) const;

        private:
            std::string _text_color;
            std::string _style_id;
            std::string _text_alignment;
            double _text_size;
            bool _text_bold;
            bool _text_italics;
            bool _text_underline;
            std::string _font_family;
        };

    }
}
