#pragma once

#include "opentime/version.h"

#include <limits>
#include <cmath>

namespace opentime {
    namespace OPENTIME_VERSION {

template <class T>
inline bool is_equal(T a, T b) {
    return std::fabs(a - b) < std::numeric_limits<T>::epsilon();
}

class Point {
public:
    Point() = default;

    Point(double x, double y)
    : _x(x), _y(y) {}

    double x() const {
        return _x;
    }

    double y() const {
        return _y;
    }

    friend bool operator== (Point lhs, Point rhs) {
        return is_equal(lhs._x, rhs._x) && is_equal(lhs._y, rhs._y);
    }

    friend bool operator!= (Point lhs, Point rhs) {
        return !(lhs == rhs);
    }

private:
    double _x{ 0.0 };
    double _y{ 0.0 };
};

} }
