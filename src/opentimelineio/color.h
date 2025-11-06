// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include <cmath>
#include <vector>

#include "opentimelineio/export.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Color consists of red, green, blue,
/// and alpha double floating point values,
/// allowing conversion between different formats.
/// To be considered interoperable,
/// the sRGB transfer function encoded values,
/// ranging between zero and one, are expected to be accurate
/// to within 1/255 of the intended value.
/// Round-trip conversions may not be guaranteed outside that.
/// This class is meant for use in user interface elements,
// like marker or clip coloring, NOT for image pixel content.
class OTIO_API_TYPE Color
{
public:
    struct Schema
    {
        static auto constexpr name   = "Color";
        static int constexpr version = 1;
    };

    OTIO_API Color(
        double const       r    = 1.f,
        double const       g    = 1.f,
        double const       b    = 1.f,
        double const       a    = 1.f,
        std::string const& name = "");

    OTIO_API Color(Color const& other);

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

    static Color* from_hex(std::string const& color);
    static Color* from_int_list(std::vector<int> const& color, int bit_depth);
    static Color* from_agbr_int(unsigned int agbr) noexcept;
    static Color* from_float_list(std::vector<double> const& color);

    friend bool operator==(Color lhs, Color rhs) noexcept
    {
        return lhs.to_hex() == rhs.to_hex()
               && lhs.to_agbr_integer() == rhs.to_agbr_integer();
    }

    OTIO_API std::string to_hex();
    OTIO_API std::vector<int> to_rgba_int_list(int base);
    OTIO_API unsigned int     to_agbr_integer();
    OTIO_API std::vector<double> to_rgba_float_list();

    double      r() const { return _r; }
    double      g() const { return _g; }
    double      b() const { return _b; }
    double      a() const { return _a; }
    std::string name() const { return _name; }

    void set_r(double r) { _r = r; }
    void set_g(double g) { _g = g; }
    void set_b(double b) { _b = b; }
    void set_a(double a) { _a = a; }
    void set_name(std::string const& name) { _name = name; }

private:
    double      _r;
    double      _g;
    double      _b;
    double      _a;
    std::string _name;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION