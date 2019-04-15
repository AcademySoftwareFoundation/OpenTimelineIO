#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentimelineio/optional.h"

class Deb : public SerializableObject {
public:
    static auto constexpr schema_name = "Deb";
    static int constexpr schema_version = 1;

    Deb()
        : some_ints { 3, 4, 5}
    {
        something_deep["key_1"] = { {1, 4, 9}, {34, 19, 20, 18} };
        metadata["alpha"] = "beta";
        metadata["gamma"] = AnyVector { 37, 13 };
    }

    bool read_from(Reader& reader) {
        bool status = SerializableObject::read_from(reader) &&
            reader.read("name", &name) &&
            reader.read("kids", &kids) &&
            reader.read("some_ints", &some_ints) &&
            reader.read("something_deep", &something_deep) &&
            reader.read("my_metadata", &metadata);

        printf("Got a good status for %s, with nkids = %zu, some_ints size is %zu\n",
               name.c_str(), kids.size(), some_ints.size());
        return status;
    }
    
    void write_to(Writer& writer) const {
        writer.write("name", name);
        writer.write("kids", kids);
        writer.write("some_ints", some_ints);
        writer.write("something_deep", something_deep);
        writer.write("my_metadata", metadata);
        SerializableObject::write_to(writer);
    }

    std::string name;
    std::vector<Deb*> kids;

    std::list<int> some_ints;
    std::map<std::string, std::list<std::vector<int>>> something_deep;
    AnyDictionary metadata;
};

void registerTypes() {
    TypeRegistry& r = TypeRegistry::instance();
    r.register_type<Deb>();
}

Deb* create_stuff() {
    Deb* x = new Deb;

    x->name = "the root";

    Deb* d0 = new Deb;
    Deb* d1 = new Deb;
    Deb* d2 = new Deb;

    d0->name = "cmw";
    d1->name = "deb";
    d2->name = "meng";

    d0->metadata["stuff1"] = true;
    d0->metadata["stuff2"] = any();
    d0->metadata["stuff3"] = 17;
    d0->metadata["stuff4"] = 3.14159;
    d0->metadata["stuff5"] = RationalTime();
    d0->metadata["stuff6"] = TimeRange();
    d0->metadata["nested"] = d0->metadata;
    
    AnyVector junk;
    junk.push_back(13);
    junk.push_back("hello");
    junk.push_back(true);
    junk.push_back(any());
    junk.push_back(any());

    x->kids.push_back(d0);
    x->kids.push_back(nullptr);
    x->kids.push_back(d1);
    x->kids.push_back(d2);
    return x;
}

void write(std::string const& file_name, SerializableObject* thing) {
    std::string errMsg;
    bool result = thing->to_json_file(file_name, &errMsg);
    if (!result) {
        printf("write error: %s\n", errMsg.c_str());
    }
}

SerializableObject* read(std::string const& file_name) {
    std::string errMsg;
    SerializableObject* thing = SerializableObject::from_json_file(file_name, &errMsg);
    if (!thing) {
        printf("read error: %s\n", errMsg.c_str());
    }
    return thing;
}

void print_it(std::vector<int> v) {
    printf("[");
    for (size_t i = 0; i < v.size(); i++) {
        if (i > 0)
            printf(", ");
        printf("%d", v[i]);
    }
    printf("]");
}

template <typename T>
void print_opt(Optional<T> const& o) {
    if (o) {
        print_it(o.value);
    }
    else {
        printf("null");
    }
    printf("\n");
}

        
typedef Optional<std::vector<int>> OptionalVecInt;
int main() {
    std::vector<int> v1 { 1, 2, 3};
    std::vector<int> v2 { 1, 2, 3, 4, 5, 6};

    OptionalVecInt ov1(v1);
    print_opt(ov1);

    OptionalVecInt ov2;
    print_opt(ov2);

    std::swap(ov1, ov2);

    print_opt(ov1);
    print_opt(ov2);

    

    


/*
    registerTypes();


    if (SerializableObject* x = read("/home/deb/sample.otio")) {
        printf("The read is ok\n");
        
        if (SerializableObject* x2 = x->clone(nullptr)) {
            printf("Type: %s\n", demangled_type_name(typeid(*x)).c_str());
            printf("Equal? %d\n", x->is_equivalent_to(*x2));
            write("/home/deb/verify.otio", x2);
        }
    }
*/

}
