// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <cmath>

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {



class Color: public SerializableObjectWithMetadata
{
public:
    struct Schema
    {
        static auto constexpr name   = "Color";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Color(double const r = 1.f,
          double const g = 1.f,
          double const b = 1.f,
          double const a = 1.f);

    Color(Color const& other);

    static const Color pink;
    static const Color red;
    static const Color orange;
    static const Color yellow;
    static const Color green;
    static const Color cyan;
    static const Color blue;
    static const Color purple;
    static const Color magenta;
    static const Color black;
    static const Color white;
    static const Color transparent;

    static Color*
    from_hex(std::string const& color) noexcept
    {
        std::string temp = color;
        if (temp[0] == '#')
        {
            temp = temp.substr(1);
        }
        else if (temp[0] == '0' and (temp[1] == 'x' or temp[1] == 'X'))
        {
            temp = temp.substr(2);
        }

        double _r, _g, _b, _a;
        // 0xFFFFFFFF (rgba, 255)
        int BASE_16 = 16;
        double BASE_16_DIV = 255.0;
        double BASE_8_DIV = 15.0;
        if (temp.length() == 8)
        {
            _r = std::stoi(temp.substr(0, 2), nullptr, BASE_16) / BASE_16_DIV;
            _g = std::stoi(temp.substr(2, 2), nullptr, BASE_16) / BASE_16_DIV;
            _b = std::stoi(temp.substr(4, 2), nullptr, BASE_16) / BASE_16_DIV;
            _a = std::stoi(temp.substr(6, 2), nullptr, BASE_16) / BASE_16_DIV;
        }
        // 0xFFFFFF (rgb, 255)
        else if (temp.length() == 6)
        {
            _r = std::stoi(temp.substr(0, 2), nullptr, BASE_16) / BASE_16_DIV;
            _g = std::stoi(temp.substr(2, 2), nullptr, BASE_16) / BASE_16_DIV;
            _b = std::stoi(temp.substr(4, 2), nullptr, BASE_16) / BASE_16_DIV;
            _a = 1.0;
        }
        // 0xFFF (rgb, 16)
        else if (temp.length() == 3)
        {
            _r = std::stoi(temp.substr(0, 1), nullptr, BASE_16) / BASE_8_DIV;
            _g = std::stoi(temp.substr(1, 1), nullptr, BASE_16) / BASE_8_DIV;
            _b = std::stoi(temp.substr(2, 1), nullptr, BASE_16) / BASE_8_DIV;
            _a = 1.0;
        }
        // 0xFFFF (rgba, 16)
        else if (temp.length() == 4)
        {
            _r = std::stoi(temp.substr(0, 1), nullptr, BASE_16) / BASE_8_DIV;
            _g = std::stoi(temp.substr(1, 1), nullptr, BASE_16) / BASE_8_DIV;
            _b = std::stoi(temp.substr(2, 1), nullptr, BASE_16) / BASE_8_DIV;
            _a = std::stoi(temp.substr(3, 1), nullptr, BASE_16) / BASE_8_DIV;
        }
        else {
            throw std::invalid_argument("Invalid hex format");
        }
        return new Color(_r, _g, _b, _a);
    }

    static Color*
    from_int_list(std::vector<int> const& color, int bit_depth) noexcept
    {
        double depth = pow(2, bit_depth) - 1.0;  // e.g. 8 = 255.0
        if (color.size() == 3)
            return new Color(color[0] / depth, color[1] / depth, color[2] / depth, 1.0);
        else if (color.size() == 4)
            return new Color(color[0] / depth, color[1] / depth, color[2] / depth, color[3] / depth);

        throw std::invalid_argument("List must have exactly 3 or 4 elements");
    }

    static Color*
    from_agbr_int(unsigned int agbr) noexcept
    {
        auto conv_r = (agbr & 0xFF) / 255.0;
        auto conv_g = ((agbr >> 16) & 0xFF) / 255.0;
        auto conv_b = ((agbr >> 8) & 0xFF) / 255.0;
        auto conv_a = ((agbr >> 24) & 0xFF) / 255.0;
        return new Color(conv_r, conv_g, conv_b, conv_a);
    }

    static Color*
    from_float_list(std::vector<double> const& color) noexcept
    {
        if (color.size() == 3)
            return new Color(color[0], color[1], color[2], 1.0);
        else if (color.size() == 4)
            return new Color(color[0], color[1], color[2], color[3]);

        throw std::invalid_argument("List must have exactly 3 or 4 elements");
    }

    friend bool
    operator==(Color lhs, Color rhs) noexcept
    {
        return lhs.to_hex() == rhs.to_hex() && lhs.to_agbr_integer() == rhs.to_agbr_integer();
    }

    std::string to_hex();
    std::vector<int> to_rgba_int_list(int base);
    unsigned int to_agbr_integer();
    std::vector<double> to_rgba_float_list();

    double r() const { return _r; }
    double g() const { return _g; }
    double b() const { return _b; }
    double a() const { return _a; }

    void set_r(double r) { _r = r; }
    void set_g(double g) { _g = g; }
    void set_b(double b) { _b = b; }
    void set_a(double a) { _a = a; }

protected:
    virtual ~Color();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    double _r;
    double _g;
    double _b;
    double _a;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION