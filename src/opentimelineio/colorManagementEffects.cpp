#include "opentimelineio/colorManagementEffects.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

bool VideoBrightness::read_from(Reader &reader)
{
    return reader.read("brightness", &_brightness)
           && Parent::read_from(reader);
}

void VideoBrightness::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("brightness", _brightness);
}

bool VideoContrast::read_from(Reader &reader)
{
    return reader.read("contrast", &_contrast)
           && Parent::read_from(reader);
}

void VideoContrast::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("contrast", _contrast);
}

bool VideoSaturation::read_from(Reader &reader)
{
    return reader.read("saturation", &_saturation)
           && Parent::read_from(reader);
}

void VideoSaturation::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("saturation", _saturation);
}

bool VideoLightness::read_from(Reader &reader)
{
    return reader.read("lightness", &_lightness)
           && Parent::read_from(reader);
}

void VideoLightness::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("lightness", _lightness);
}

bool VideoColorTemperature::read_from(Reader &reader)
{
    return reader.read("temperature", &_temperature)
           && Parent::read_from(reader);
}

void VideoColorTemperature::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("temperature", _temperature);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
