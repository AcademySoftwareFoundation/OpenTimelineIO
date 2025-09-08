#include "opentimelineio/transformEffects.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
bool VideoScale::read_from(Reader &reader)
{
    return reader.read("width", &_width)
           && reader.read("height", &_height)
           && Parent::read_from(reader);
}

void VideoScale::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("width", _width);
    writer.write("height", _height);
}

bool VideoCrop::read_from(Reader &reader)
{
    return reader.read("left", &_left)
           && reader.read("right", &_right)
           && reader.read("top", &_top)
           && reader.read("bottom", &_bottom)
           && Parent::read_from(reader);
}

void VideoCrop::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("left", _left);
    writer.write("right", _right);
    writer.write("top", _top);
    writer.write("bottom", _bottom);
}

bool VideoPosition::read_from(Reader &reader)
{
    return reader.read("x", &_x)
           && reader.read("y", &_y)
           && Parent::read_from(reader);
}

void VideoPosition::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("x", _x);
    writer.write("y", _y);
}

bool VideoRotate::read_from(Reader &reader)
{
    return reader.read("angle", &_angle)
           && Parent::read_from(reader);
}

void VideoRotate::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("angle", _angle);
}

bool VideoRoundedCorners::read_from(Reader &reader)
{
    return reader.read("radius", &_radius)
           && Parent::read_from(reader);
}

void VideoRoundedCorners::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("radius", _radius);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
