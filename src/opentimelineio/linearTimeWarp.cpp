#include "opentimelineio/linearTimeWarp.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
LinearTimeWarp::LinearTimeWarp(std::string const& name,
                               double time_scalar,
                               AnyDictionary const& metadata)
    : Parent(name, "LinearTimeWarp", metadata),
      _time_scalar(time_scalar) {
}

LinearTimeWarp::~LinearTimeWarp() {
}

bool LinearTimeWarp::read_from(Reader& reader) {
    return reader.read("time_scalar", &_time_scalar) &&
        Parent::read_from(reader);
}

void LinearTimeWarp::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("time_scalar", _time_scalar);
}

} }
