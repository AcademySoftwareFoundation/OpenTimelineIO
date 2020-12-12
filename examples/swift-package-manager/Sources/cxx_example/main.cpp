#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/anyVector.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentimelineio/optional.h"

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

otio::SerializableObject* create_stuff() {
    auto x = new otio::SerializableObjectWithMetadata;

    x->set_name("the root");

    x->metadata()["stuff1"] = true;
    x->metadata()["stuff3"] = 17;
    x->metadata()["stuff4"] = 3.14159;
    x->metadata()["stuff5"] = opentime::RationalTime();
    x->metadata()["stuff6"] = opentime::TimeRange();
    
    otio::AnyVector junk;
    junk.push_back(13);
    junk.push_back("hello");
    junk.push_back(true);
    return x;
}

int main() {
    auto so = create_stuff();
    otio::ErrorStatus status;
    std::string s = so->to_json_string(&status);
    printf("%s\n", s.c_str());
}

