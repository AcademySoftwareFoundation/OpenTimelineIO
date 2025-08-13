// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <iomanip>
#include <sstream>

#include "opentimelineio/color.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Color::Color(
    double const         r,
    double const         g,
    double const         b,
    double const         a,
    std::string const&   name)
    : _name(name),
    _r(r),
    _g(g),
    _b(b),
    _a(a) {}

Color::Color(Color const& other) : _name(other.name()),
                                   _r(other.r()),
                                   _g(other.g()),
                                   _b(other.b()),
                                   _a(other.a()) {}

const Color Color::pink(1.0, 0.0, 1.0, 1.0, "Pink");
const Color Color::red(1.0, 0.0, 0.0, 1.0, "Red");
const Color Color::orange(1.0, 0.5, 0.0, 1.0, "Orange");
const Color Color::yellow(1.0, 1.0, 0.0, 1.0, "Yellow");
const Color Color::green(0.0, 1.0, 0.0, 1.0, "Green");
const Color Color::cyan(0.0, 1.0, 1.0, 1.0, "Cyan");
const Color Color::blue(0.0, 0.0, 1.0, 1.0, "Blue");
const Color Color::purple(0.5, 0.0, 0.5, 1.0, "Purple");
const Color Color::magenta(1.0, 0.0, 1.0, 1.0, "Magenta");
const Color Color::black(0.0, 0.0, 0.0, 1.0, "Black");
const Color Color::white(1.0, 1.0, 1.0, 1.0, "White");
const Color Color::transparent(1.0, 1.0, 1.0, 0.0, "Transparent");

Color*
Color::from_hex(std::string const& color)
{
    std::string temp = color;
    if (temp[0] == '#')
    {
        temp = temp.substr(1);
    }
    else if (temp[0] == '0' && (temp[1] == 'x' || temp[1] == 'X'))
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

Color*
Color::from_int_list(std::vector<int> const& color, int bit_depth)
{
    double depth = pow(2, bit_depth) - 1.0;  // e.g. 8 = 255.0
    if (color.size() == 3)
        return new Color(color[0] / depth, color[1] / depth, color[2] / depth, 1.0);
    else if (color.size() == 4)
        return new Color(color[0] / depth, color[1] / depth, color[2] / depth, color[3] / depth);

    throw std::invalid_argument("List must have exactly 3 or 4 elements");
}

Color*
Color::from_agbr_int(unsigned int agbr) noexcept
{
    auto conv_r = (agbr & 0xFF) / 255.0;
    auto conv_g = ((agbr >> 16) & 0xFF) / 255.0;
    auto conv_b = ((agbr >> 8) & 0xFF) / 255.0;
    auto conv_a = ((agbr >> 24) & 0xFF) / 255.0;
    return new Color(conv_r, conv_g, conv_b, conv_a);
}

Color*
Color::from_float_list(std::vector<double> const& color)
{
    if (color.size() == 3)
        return new Color(color[0], color[1], color[2], 1.0);
    else if (color.size() == 4)
        return new Color(color[0], color[1], color[2], color[3]);

    throw std::invalid_argument("List must have exactly 3 or 4 elements");
}

std::string
Color::to_hex()
{
    auto rgba = to_rgba_int_list(8);
    std::stringstream ss;
    ss << "#";

    ss << std::hex << std::setfill('0');
    ss << std::setw(2) << rgba[0];
    ss << std::setw(2) << rgba[1];
    ss << std::setw(2) << rgba[2];
    ss << std::setw(2) << rgba[3];
    return ss.str();
}

std::vector<int>
Color::to_rgba_int_list(int base)
{
    double math_base = pow(2, base) - 1.0;
    return {int(_r * math_base), int(_g * math_base), int(_b * math_base), int(_a * math_base)};
}

unsigned int
Color::to_agbr_integer()
{
    auto rgba = to_rgba_int_list(8);
    return (rgba[3] << 24) + (rgba[2] << 16) + (rgba[1] << 8) + rgba[0];
}

std::vector<double>
Color::to_rgba_float_list()
{
    return {_r, _g, _b, _a};
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION