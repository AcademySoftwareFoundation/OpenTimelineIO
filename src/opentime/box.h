#pragma once

#include "opentime/version.h"
#include "opentime/point.h"

namespace opentime {
    namespace OPENTIME_VERSION {

class Box {
public:
    Box() = default;

    Box(double width, double height, Point const& center)
    : _width(width), _height(height), _center(center) {}

    double width() const {
        return _width;
    }

    double height() const {
        return _height;
    }

    Point const& center() const {
        return _center;
    }

    double get_aspect_ratio() const {
        return is_equal( _height, 0.0 ) ? 1.0 : _width / _height;
    }

    bool contains(Point const& p) const {
       static constexpr auto epsilon = std::numeric_limits<double>::epsilon();

       const double min_x = _center.x() - _width * 0.5 - epsilon;
       const double max_x = _center.x() + _width * 0.5 + epsilon;

       if (p.x() < min_x || p.x() > max_x) return false;

       const double min_y = _center.y() - _height * 0.5 - epsilon;
       const double max_y = _center.y() + _height * 0.5 + epsilon;

       return p.y() >= min_y && p.y() <= max_y;
    }

    Box get_union(Box const& b) const {
        const double min_x = std::min(_center.x() - _width * 0.5,
                                      b._center.x() - b._width * 0.5);
        const double max_x = std::max(_center.x() + _width * 0.5,
                                      b._center.x() + b._width * 0.5);
        const double min_y = std::min(_center.y() - _height * 0.5,
                                      b._center.y() - b._height * 0.5);
        const double max_y = std::max(_center.y() + _height * 0.5,
                                      b._center.y() + b._height * 0.5);

        return Box(max_x - min_x, max_y - min_y,
                   Point((max_x + min_x) * 0.5, (max_y + min_y) * 0.5));
    }

    friend bool operator== (Box lhs, Box rhs) {
        return is_equal( lhs._width, rhs._width ) &&
               is_equal( lhs._height, rhs._height ) &&
               lhs._center == rhs._center;
    }

    friend bool operator!= (Box lhs, Box rhs) {
        return !(lhs == rhs);
    }

private:
    double _width{ 0.0 };
    double _height{ 0.0 };
    Point _center;
};

} }
