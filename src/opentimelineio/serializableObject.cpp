// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/serializableObject.h"
#include "opentimelineio/deserialization.h"
#include "opentimelineio/serialization.h"
#include "stringUtils.h"
#include "typeRegistry.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

SerializableObject::SerializableObject()
    : _cached_type_record(nullptr)
{
    _managed_ref_count = 0;
}

SerializableObject::~SerializableObject()
{}

// forwarded functions
std::string
SerializableObject::Reader::fwd_type_name_for_error_message(
    std::type_info const& t)
{
    return type_name_for_error_message(t);
}
std::string
SerializableObject::Reader::fwd_type_name_for_error_message(std::any const& a)
{
    return type_name_for_error_message(a);
}
std::string
SerializableObject::Reader::fwd_type_name_for_error_message(
    class SerializableObject* so)
{
    return type_name_for_error_message(so);
}

TypeRegistry::_TypeRecord const*
SerializableObject::_type_record() const
{
    std::lock_guard<std::mutex> lock(_mutex);
    if (!_cached_type_record)
    {
        _cached_type_record =
            TypeRegistry::instance()._lookup_type_record(typeid(*this));
        if (!_cached_type_record)
        {
            fatal_error(string_printf(
                "Code for C++ type %s has not been registered via "
                "TypeRegistry::register_type<T>()",
                type_name_for_error_message(typeid(*this)).c_str()));
        }
    }

    return _cached_type_record;
}

bool
SerializableObject::_is_deletable()
{
    std::lock_guard<std::mutex> lock(_mutex);
    return _managed_ref_count == 0;
}

bool
SerializableObject::possibly_delete()
{
    if (!_is_deletable())
    {
        return false;
    }
    delete this;
    return true;
}

bool
SerializableObject::read_from(Reader& reader)
{
    /*
     * Want to move everything from reader._dict into
     * _dynamic_fields, overwriting as we go.
     */
    for (auto& e: reader._dict)
    {
        auto it = _dynamic_fields.find(e.first);
        if (it != _dynamic_fields.end())
        {
            it->second.swap(e.second);
        }
        else
        {
            _dynamic_fields.emplace(e.first, std::move(e.second));
        }
    }
    return true;
}

void
SerializableObject::write_to(Writer& writer) const
{
    for (auto e: _dynamic_fields)
    {
        writer.write(e.first, e.second);
    }
}

bool
SerializableObject::is_unknown_schema() const
{
    return false;
}

std::string
SerializableObject::to_json_string(
    ErrorStatus*              error_status,
    const schema_version_map* schema_version_targets,
    int                       indent) const
{
    return serialize_json_to_string(
        std::any(Retainer<>(this)),
        schema_version_targets,
        error_status,
        indent);
}

bool
SerializableObject::to_json_file(
    std::string const&        file_name,
    ErrorStatus*              error_status,
    const schema_version_map* schema_version_targets,
    int                       indent) const
{
    return serialize_json_to_file(
        std::any(Retainer<>(this)),
        file_name,
        schema_version_targets,
        error_status,
        indent);
}

SerializableObject*
SerializableObject::from_json_string(
    std::string const& input,
    ErrorStatus*       error_status)
{
    std::any dest;

    if (!deserialize_json_from_string(input, &dest, error_status))
    {
        return nullptr;
    }

    if (dest.type() != typeid(Retainer<>))
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::TYPE_MISMATCH,
                string_printf(
                    "Expected a SerializableObject*, found object of type '%s' instead",
                    type_name_for_error_message(dest.type()).c_str()));
        }
        return nullptr;
    }

    return std::any_cast<Retainer<>&>(dest).take_value();
}

SerializableObject*
SerializableObject::from_json_file(
    std::string const& file_name,
    ErrorStatus*       error_status)
{
    std::any dest;

    if (!deserialize_json_from_file(file_name, &dest, error_status))
    {
        return nullptr;
    }

    if (dest.type() != typeid(Retainer<>))
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::TYPE_MISMATCH,
                string_printf(
                    "Expected a SerializableObject*, found object of type '%s' instead",
                    type_name_for_error_message(dest.type()).c_str()));
        }
        return nullptr;
    }

    return std::any_cast<Retainer<>&>(dest).take_value();
}

std::string
SerializableObject::_schema_name_for_reference() const
{
    return schema_name();
}

void
SerializableObject::_managed_retain()
{
    {
        std::lock_guard<std::mutex> lock(_mutex);
        if (_managed_ref_count++ != 1 || !_external_keepalive_monitor)
            return;
    }

    // We just changed from unique (old ref count was 1) to non-unique
    // and we know we have a monitor.
    _external_keepalive_monitor();
}

void
SerializableObject::_managed_release()
{
    _mutex.lock();

    if (--_managed_ref_count == 0)
    {
        _mutex.unlock();
        delete this;
        return;
    }

    if (_managed_ref_count != 1 || !_external_keepalive_monitor)
    {
        _mutex.unlock();
        return;
    }

    // We just changed back to unique (new ref count is 1)
    // and we know we have a monitor.

    _mutex.unlock();
    _external_keepalive_monitor();
}

void
SerializableObject::install_external_keepalive_monitor(
    std::function<void()> monitor,
    bool                  apply_now)
{
    {
        std::lock_guard<std::mutex> lock(_mutex);
        if (!_external_keepalive_monitor)
        {
            _external_keepalive_monitor = monitor;
        }
    }

    if (apply_now)
    {
        _external_keepalive_monitor();
    }
}

int
SerializableObject::current_ref_count() const
{
    std::lock_guard<std::mutex> lock(_mutex);
    return _managed_ref_count;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
