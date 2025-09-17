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

bool VideoFlip::read_from(Reader &reader)
{
    return reader.read("flip_horizontally", &_flip_horizontally)
           && reader.read("flip_vertically", &_flip_vertically)
           && Parent::read_from(reader);
}

void VideoFlip::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("flip_horizontally", _flip_horizontally);
    writer.write("flip_vertically", _flip_vertically);
}

bool VideoMask::read_from(Reader &reader)
{
    bool result = reader.read("mask_type", &_mask_type)
           && reader.read("mask_url", &_mask_url)
           && reader.read_if_present("mask_replacement_url", &_mask_replacement_url)
           && reader.read_if_present("blur_radius", &_blur_radius)
           && Parent::read_from(reader);

    if (result) {
        // Check optionals are present for the mask type
        if (_mask_type == MaskType::replace) {
            if (!_mask_replacement_url) {
                return false;
            }
        } else if (_mask_type == MaskType::blur) {
            if (!_blur_radius) {
                return false;
            }
        }
    }

    return result;
}

void VideoMask::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("mask_type", _mask_type);
    writer.write("mask_url", _mask_url);
    if (_mask_replacement_url) {
        writer.write("mask_replacement_url", _mask_replacement_url.value());
    }
    if (_blur_radius) {
        writer.write("blur_radius", _blur_radius.value());
    }
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
