#include "opentimelineio/typeRegistry.h"

#include "opentimelineio/clip.h"
#include "opentimelineio/composable.h"
#include "opentimelineio/composition.h"
#include "opentimelineio/effect.h"
#include "opentimelineio/externalReference.h"
#include "opentimelineio/freezeFrame.h"
#include "opentimelineio/gap.h"
#include "opentimelineio/generatorReference.h"
#include "opentimelineio/imageSequenceReference.h"
#include "opentimelineio/item.h"
#include "opentimelineio/linearTimeWarp.h"
#include "opentimelineio/marker.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/missingReference.h"
#include "opentimelineio/serializableCollection.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/stack.h"
#include "opentimelineio/timeEffect.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/track.h"
#include "opentimelineio/transition.h"
#include "opentimelineio/unknownSchema.h"
#include "stringUtils.h"

#include <assert.h>
#include <vector>
//#include <sstream>
//#include <iostream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

TypeRegistry&
TypeRegistry::TypeRegistry::instance()
{
    static TypeRegistry r;
    return r;
}

TypeRegistry::TypeRegistry()
{
    register_type(
        UnknownSchema::Schema::name,
        UnknownSchema::Schema::version,
        &typeid(UnknownSchema),
        []() {
            fatal_error(
                "UnknownSchema should not be created from type registry");
            return nullptr;
        },
        "UnknownSchema");

    register_type<Clip>();
    register_type<Composable>();
    register_type<Composition>();
    register_type<Effect>();
    register_type<ExternalReference>();
    register_type<FreezeFrame>();

    register_type<Gap>();
    register_type_from_existing_type("Filler", 1, "Gap", nullptr);

    register_type<GeneratorReference>();
    register_type<ImageSequenceReference>();
    register_type<Item>();
    register_type<LinearTimeWarp>();
    register_type<Marker>();
    register_type<MediaReference>();
    register_type<MissingReference>();

    register_type<SerializableObject>();
    register_type<SerializableObjectWithMetadata>();
    register_type<SerializableCollection>();
    register_type_from_existing_type(
        "SerializeableCollection", 1, "SerializableCollection", nullptr);

    register_type<Stack>();
    register_type<TimeEffect>();
    register_type<Timeline>();
    register_type<Track>();
    register_type_from_existing_type("Sequence", 1, "Track", nullptr);
    register_type<Transition>();

    /*
     * Upgrade functions:
     */
    register_upgrade_function(Marker::Schema::name, 2, [](AnyDictionary* d) {
        (*d)["marked_range"] = (*d)["range"];
        d->erase("range");
    });
}

bool
TypeRegistry::register_type(
    std::string const&                   schema_name,
    int                                  schema_version,
    std::type_info const*                type,
    std::function<SerializableObject*()> create,
    std::string const&                   class_name)
{
    std::lock_guard<std::mutex> lock(_registry_mutex);

    if (!_find_type_record(schema_name))
    {
        _TypeRecord* r =
            new _TypeRecord{ schema_name, schema_version, class_name, create };
        _type_records[schema_name] = r;
        if (type)
        {
            _type_records_by_type_name[type->name()] = r;
        }
        return true;
    }
    return false;
}

bool
TypeRegistry::register_type_from_existing_type(
    std::string const& schema_name,
    int /* schema_version */,
    std::string const& existing_schema_name,
    ErrorStatus*       error_status)
{
    std::lock_guard<std::mutex> lock(_registry_mutex);
    if (auto r = _find_type_record(existing_schema_name))
    {
        if (!_find_type_record(schema_name))
        {
            _type_records[schema_name] = new _TypeRecord{
                r->schema_name, r->schema_version, r->class_name, r->create
            };
            return true;
        }

        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::SCHEMA_ALREADY_REGISTERED, schema_name);
        }
        return false;
    }

    if (error_status)
    {
        *error_status = ErrorStatus(
            ErrorStatus::SCHEMA_NOT_REGISTERED,
            string_printf(
                "cannot define schema %s in terms of %s; %s has not been registered",
                schema_name.c_str(),
                existing_schema_name.c_str(),
                existing_schema_name.c_str()));
    }
    return false;
}

bool
TypeRegistry::register_upgrade_function(
    std::string const&                  schema_name,
    int                                 version_to_upgrade_to,
    std::function<void(AnyDictionary*)> upgrade_function)
{
    std::lock_guard<std::mutex> lock(_registry_mutex);
    if (auto r = _find_type_record(schema_name))
    {
        if (r->upgrade_functions.find(version_to_upgrade_to) ==
            r->upgrade_functions.end())
        {
            r->upgrade_functions[version_to_upgrade_to] = upgrade_function;
            return true;
        }
    }

    return false;
}

SerializableObject*
TypeRegistry::_instance_from_schema(
    std::string    schema_name,
    int            schema_version,
    AnyDictionary& dict,
    bool           internal_read,
    ErrorStatus*   error_status)
{
    _TypeRecord const* type_record;
    bool               create_unknown = false;

    {
        std::lock_guard<std::mutex> lock(_registry_mutex);
        type_record = _find_type_record(schema_name);

        if (!type_record)
        {
            create_unknown = true;
            type_record    = _find_type_record(UnknownSchema::Schema::name);
            assert(type_record);
        }
    }

    SerializableObject* so;
    if (create_unknown)
    {
        so             = new UnknownSchema(schema_name, schema_version);
        schema_name    = type_record->schema_name;
        schema_version = type_record->schema_version;
    }
    else
    {
        so = type_record->create_object();
    }

    if (schema_version > type_record->schema_version)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::SCHEMA_VERSION_UNSUPPORTED,
                string_printf(
                    "Schema %s has highest version %d, but the requested "
                    "schema version %d is even greater.",
                    schema_name.c_str(),
                    type_record->schema_version,
                    schema_version));
        }
        return nullptr;
    }
    else if (schema_version < type_record->schema_version)
    {
        for (auto e: type_record->upgrade_functions)
        {
            if (schema_version <= e.first &&
                e.first <= type_record->schema_version)
            {
                e.second(&dict);
            }
        }
    }

    if (internal_read)
    {
        return so;
    }

    auto error_function = [error_status](ErrorStatus const& status) {
        if (error_status)
        {
            *error_status = status;
        }
    };

    // g++ compiler bug if we pass error_function directly into Reader
    std::function<void(ErrorStatus const&)> ef = error_function;
    SerializableObject::Reader              r(dict, ef, nullptr);
    return so->read_from(r) ? so : nullptr;
}

TypeRegistry::_TypeRecord*
TypeRegistry::_lookup_type_record(std::string const& schema_name)
{
    std::lock_guard<std::mutex> lock(_registry_mutex);
    auto                        e = _type_records.find(schema_name);
    return e != _type_records.end() ? e->second : nullptr;
}

TypeRegistry::_TypeRecord*
TypeRegistry::_lookup_type_record(std::type_info const& type)
{
    std::lock_guard<std::mutex> lock(_registry_mutex);
    auto e = _type_records_by_type_name.find(type.name());
    return e != _type_records_by_type_name.end() ? e->second : nullptr;
}

SerializableObject*
TypeRegistry::_TypeRecord::create_object() const
{
    SerializableObject* so = create();
    so->_set_type_record(this);
    return so;
}

bool
TypeRegistry::set_type_record(
    SerializableObject* so,
    std::string const&  schema_name,
    ErrorStatus*        error_status)
{
    auto r = _lookup_type_record(schema_name);
    if (r)
    {
        so->_set_type_record(r);
        return true;
    }

    if (error_status)
    {
        *error_status = ErrorStatus(
            ErrorStatus::SCHEMA_NOT_REGISTERED,
            string_printf(
                "Cannot set type record on instance of type %s: schema %s unregistered",
                type_name_for_error_message(so).c_str(),
                schema_name.c_str()));
    }
    return false;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
