#ifndef OTIO_SERIALIZABLEOBJECT_H
#define OTIO_SERIALIZABLEOBJECT_H

#include "anyVector.h"
#include "anyDictionary.h"
#include "optional.hpp"
#include "typeRegistry.h"
#include "stringUtils.h"
#include "rationalTime.h"
#include "timeRange.h"
#include <type_traits>
#include <assert.h>
#include <list>

class SerializableObject {
public:
    struct Schema {
        static auto constexpr name = "SerializableObject";
        static int constexpr version = 1;
    };

    SerializableObject();

    /*
     * You cannot directly delete a SerializableObject* (or, hopefully, anything
     * derived from it, as all derivations are required to protect the destructor).
     *
     * Instead, call the member funtion possibly_delete(), which deletes the object
     * (and, recursively, the objects owned by this object), provided the objects
     * are not under external management (e.g. prevented from being deleted because an
     * external scripting system is holding a reference to them).
     */
    bool possibly_delete();

    // Serialize this schema to file_name.  Schema instances reachable from this
    // schema are serialized as well.
    bool to_json_file(std::string const& file_name, std::string* err_msg, int indent = 4) const;

    // Return the serialization of this schema as a string. Schema instances reachable from this
    // schema are serialized as well.
    std::string to_json_string(std::string* err_msg, int indent = 4) const;

    // Return the schema instance that was serialized into file_name.  Schema instances that
    // are referred to by this schema (and so on) will come along for the ride as well.
    //
    // If the operation fails, nullptr is returned and err_msg is
    // set appropriately.
    static SerializableObject* from_json_file(std::string const& file_name, std::string* err_msg);

    // Return the schema instance that was serialized into string.  Schema instances that
    // are referred to by this schema (and so on) will come along for the ride as well.
    //
    // If the operation fails, nullptr is returned and err_msg is
    // set appropriately.
    static SerializableObject* from_json_string(std::string const& input, std::string* err_msg);

    // Return true if *this is equivalent to other.
    //
    // Two schemas are equivalent if they hold exactly the same set of properties and if
    // the values of each property are equivalent, using '==' for everything except schema
    // comparison and using (recursively) is_equivalent_to() for schema equivalence.
    //
    // If the operation fails, false is returned and err_msg is
    // set appropriately.
    bool is_equivalent_to(SerializableObject const& other) const;

    // Makes a (deep) clone of this instance.
    //
    // Any schema instances referred to by properties in *this are cloned, and so on.
    //
    // If the operation fails, nullptr is returned and err_msg is
    // set appropriately.
    SerializableObject* clone(std::string* err_msg = nullptr) const;

    // Read-access to schema name
    std::string const& schema_name() const {
        return _type_record()->schema_name;
    }

    // Read-access to schema version
    int schema_version() const {
        return _type_record()->schema_version;
    }

    class Reader {
        ...
    }:
    
    class Writer {
        ...
    };

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

    // Allow external system (e.g. Python, Swifft) to add serializable fields
    // on the fly.  C++ implementations should have no need for this functionality.
    AnyDictionary& dynamic_fields() {
        return _dynamic_fields;
    }

    template <typename T>
    struct Retainer {
        operator T* () const;
        operator bool () const;

        Retainer(T const* so = nullptr);
        Retainer(Retainer const& rhs);
        Retainer& operator=(Retainer const& rhs);
        ~Retainer();

        // Decrements count on pointed to object, return it, and set value to nullptr.
        // However, does NOT delete pointed to object if count falls to zero.  In this case,
        // the caller takes responsibility for deleting the returned instance.
        T* take_value();
        T* value;
    };
    

    // For external bridges.  Not needed by C++ implementations.
    void install_external_keepalive_monitor(std::function<void (bool)> monitor, bool apply_now);
};



#endif
