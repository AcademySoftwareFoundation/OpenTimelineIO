// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <iomanip>
#include <sstream>

#include "opentimelineio/color.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Color::Color(
    double const r,
    double const g,
    double const b,
    double const a)
    : _r(r),
    _g(g),
    _b(b),
    _a(a) {}

Color::Color(Color const& other) : _r(other.r()),
                                   _g(other.g()),
                                   _b(other.b()),
                                   _a(other.a()) {}

const Color Color::pink(1.0, 0.0, 1.0, 1.0);
const Color Color::red(1.0, 0.0, 0.0, 1.0);
const Color Color::orange(1.0, 0.5, 0.0, 1.0);
const Color Color::yellow(1.0, 1.0, 0.0, 1.0);
const Color Color::green(0.0, 1.0, 0.0, 1.0);
const Color Color::cyan(0.0, 1.0, 1.0, 1.0);
const Color Color::blue(0.0, 0.0, 1.0, 1.0);
const Color Color::purple(0.5, 0.0, 0.5, 1.0);
const Color Color::magenta(1.0, 0.0, 1.0, 1.0);
const Color Color::black(0.0, 0.0, 0.0, 1.0);
const Color Color::white(1.0, 1.0, 1.0, 1.0);
const Color Color::transparent(0.0, 0.0, 0.0, 0.0);

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

std::array<int, 4>
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

std::array<double, 4>
Color::to_rgba_float_list()
{
    return {_r, _g, _b, _a};
}

Color::~Color()
{}

bool
Color::read_from(Reader& reader)
{
    return reader.read("r", &_r)
                && reader.read("g", &_g)
                && reader.read("b", &_b)
                && reader.read("a", &_a)
                && Parent::read_from(reader);
}

void
Color::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("r", _r);
    writer.write("g", _g);
    writer.write("b", _b);
    writer.write("a", _a);
}
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION