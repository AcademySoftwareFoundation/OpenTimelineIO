#include "serializableObject.h"

class UnknownSchema : public SerializableObject {
public:
    struct Schema {
        static auto constexpr name = "UnknownSchema";
        static int constexpr version = 1;
    };

    UnknownSchema(std::string original_schema_name, int original_schema_version)
        : _original_schema_name(original_schema_name),
          _original_schema_version(original_schema_version)
    {
    }

    std::string const& original_schema_name() const;
    int original_schema_version() const;

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    virtual ~UnknownSchema();

    virtual std::string const& _schema_name_for_reference() const;

    std::string _original_schema_name;
    int _original_schema_version;

    AnyDictionary _data;
};
