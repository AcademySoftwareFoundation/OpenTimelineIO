#include "opentimelineio/serializableObject.h"
#include "opentimelineio/unknownSchema.h"
#include "opentimelineio/stringUtils.h"

#define RAPIDJSON_NAMESPACE OTIO_rapidjson
#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <rapidjson/prettywriter.h>
#include <rapidjson/ostreamwrapper.h>
#include <fstream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
/*
 * Base class for encoders.  Since rapidjson is templated (no virtual functions)
 * we need to do our dynamically classed hierarchy to abstract away which writer
 * we are using.  This also lets us create the CloningEncoder, which is what
 * we use not to serialize a class, but to copy it in memory, thereby cloning
 * an instance of a SerializableObject.
 *
 * This hierarchy is not visible outside this library, so we're not very concerned
 * about access control within this class.
 */
class Encoder {
public:
    virtual ~Encoder() {
    }

    bool has_errored(ErrorStatus* error_status) {
        *error_status = _error_status;
        return bool(_error_status);
    }
        
    bool has_errored() {
        return bool(_error_status);
    }
    

    virtual void start_object() = 0;
    virtual void end_object() = 0;

    virtual void start_array(size_t) = 0;
    virtual void end_array() = 0;

    virtual void write_key(std::string const& key) = 0;
    virtual void write_null_value() = 0;
    virtual void write_value(bool value) = 0;
    virtual void write_value(int value) = 0;
    virtual void write_value(int64_t value) = 0;
    virtual void write_value(double value) = 0;
    virtual void write_value(std::string const& value) = 0;
    virtual void write_value(class RationalTime const& value) = 0;
    virtual void write_value(class TimeRange const& value) = 0;
    virtual void write_value(class TimeTransform const& value) = 0;
    virtual void write_value(struct SerializableObject::ReferenceId) = 0;

protected:
    void _error(ErrorStatus const& error_status) {
        _error_status = error_status;
    }

private:
    friend class SerializableObject;
    ErrorStatus _error_status;
};

/*
 * This encoder builds up a dictionary as its method of "encoding".
 * The dictionary is than handed off to a CloningDecoder, to complete
 * copying of a SerializableObject instance.
 */
class CloningEncoder : public Encoder {
public:
    CloningEncoder(bool actually_clone) {
        using namespace std::placeholders;
        _error_function = std::bind(&CloningEncoder::_error, this, _1);
        _actually_clone = actually_clone;
    }

    virtual ~CloningEncoder() {
    }

    void write_key(std::string const& key) {
        if (has_errored()) {
            return;
        }
        
        if (_stack.empty() || !_stack.back().is_dict) {
            _internal_error("Encoder::write_key  called while not decoding an object");
            return;
        }

        _stack.back().cur_key = key;
    }

    void _store(any&& a) {
        if (has_errored()) {
            return;
        }
        
        if (_stack.empty()) {
            _root.swap(a);
        }
        else {
            auto& top = _stack.back();
            if (top.is_dict) {
                top.dict.emplace(_stack.back().cur_key, a);
            }
            else {
                top.array.emplace_back(a);
            }
        }
    }

    void write_null_value() {
        _store(any());
    }

    void write_value(bool value) {
        _store(any(value));
    }

    void write_value(int value) {
        _store(any(value));
    }

    void write_value(int64_t value) {
        _store(any(value));
    }

    void write_value(std::string const& value) {
        _store(any(value));
    }

    void write_value(double value) {
        _store(any(value));
    }

    void write_value(RationalTime const& value) {
        _store(any(value));
    }

    void write_value(TimeRange const& value) {
        _store(any(value));
    }

    void write_value(TimeTransform const& value) {
        _store(any(value));
    }
    
    void write_value(SerializableObject::ReferenceId value) {
        _store(any(value));
    }

    void start_array(size_t /* n */) {
        if (has_errored()) {
            return;
        }
        
        _stack.emplace_back(_DictOrArray { false /* is_dict*/ });
    }
    
    void start_object() {
        if (has_errored()) {
            return;
        }
        
        _stack.emplace_back(_DictOrArray { true /* is_dict*/ });
    }

    void end_array() {
        if (has_errored()) {
            return;
        }

        if (_stack.empty()) {
            _internal_error("Encoder::end_array() called without matching start_array()");
        }
        else {
            auto& top = _stack.back();
            if (top.is_dict) {
                _internal_error("Encoder::end_array() called without matching start_array()");
                _stack.pop_back();
            }
            else {
                AnyVector va;
                va.swap(top.array);
                _stack.pop_back();
                _store(any(std::move(va)));
            }

        }
    }

    void end_object() {
        if (has_errored()) {
            return;
        }

        if (_stack.empty()) {
            _internal_error("Encoder::end_object() called without matching start_object()");
        }
        else {
            auto& top = _stack.back();
            if (!top.is_dict) {
                _internal_error("Encoder::end_object() called without matching start_object()");
                _stack.pop_back();
            }
            else {
                /*
                 * Convert back to SerializableObject* right here.
                 */
                if (_actually_clone) {
                    SerializableObject::Reader reader(top.dict, _error_function, nullptr);
                    _stack.pop_back();
                    _store(reader._decode(_resolver));
                }
                else {
                    AnyDictionary m;
                    m.swap(top.dict);
                    _stack.pop_back();
                    _store(any(std::move(m)));
                }
            }
        }
    }

private:
    any _root;
    SerializableObject::Reader::_Resolver _resolver;
    std::function<void (ErrorStatus const&)> _error_function;

    struct _DictOrArray {
        _DictOrArray(bool is_dict) {
            this->is_dict = is_dict;
        }
        
        bool is_dict;
        AnyDictionary dict;
        AnyVector array;
        std::string cur_key;
    };

    void _internal_error(std::string const& err_msg) {
        _error(ErrorStatus(ErrorStatus::INTERNAL_ERROR, err_msg));
    }


    friend class SerializableObject;
    std::vector<_DictOrArray> _stack;
    bool _actually_clone;
};


template <typename RapidJSONWriterType>
class JSONEncoder : public Encoder {
public:
    JSONEncoder(RapidJSONWriterType& writer)
        : _writer(writer) {
    }
    
    virtual ~JSONEncoder() {
    }

    void write_key(std::string const& key) {
        _writer.Key(key.c_str());
    }

    void write_null_value() {
        _writer.Null();
    }

    void write_value(bool value) {
        _writer.Bool(value);
    }

    void write_value(int value) {
        _writer.Int(value);
    }

    void write_value(int64_t value) {
        _writer.Int64(value);
    }

    void write_value(std::string const& value) {
        _writer.String(value.c_str());
    }

    void write_value(double value) {
        _writer.Double(value);

    }

    void write_value(RationalTime const& value) {
        _writer.StartObject();

        _writer.Key("OTIO_SCHEMA");
        _writer.String("RationalTime.1");

        _writer.Key("rate");
        _writer.Double(value.rate());

        _writer.Key("value");
        _writer.Double(value.value());
        
        _writer.EndObject();
    }

    void write_value(TimeRange const& value) {
        _writer.StartObject();

        _writer.Key("OTIO_SCHEMA");
        _writer.String("TimeRange.1");

        _writer.Key("duration");
        write_value(value.duration());
        
        _writer.Key("start_time");
        write_value(value.start_time());

        _writer.EndObject();
    }

    void write_value(TimeTransform const& value) {
        _writer.StartObject();

        _writer.Key("OTIO_SCHEMA");
        _writer.String("TimeTransform.1");

        _writer.Key("offset");
        write_value(value.offset());
        
        _writer.Key("rate");
        _writer.Double(value.rate());

        _writer.Key("scale");
        _writer.Double(value.scale());

        _writer.EndObject();
    }
    
    void write_value(SerializableObject::ReferenceId value) {
        _writer.StartObject();
        _writer.Key("OTIO_SCHEMA");
        _writer.String("SerializableObjectRef.1");
        _writer.Key("id");
        _writer.String(value.id.c_str());
        _writer.EndObject();
    }

    void start_array(size_t) {
        _writer.StartArray();
    }
    
    void start_object() {
        _writer.StartObject();
    }

    void end_array() {
        _writer.EndArray();
    }

    void end_object() {
        _writer.EndObject();
    }

private:
    RapidJSONWriterType& _writer;
};

template <typename T>
bool _simple_any_comparison(any const& lhs, any const& rhs) {
    return lhs.type() == typeid(T) && rhs.type() == typeid(T) &&
        any_cast<T const&>(lhs) == any_cast<T const&>(rhs);
}

template <>
bool _simple_any_comparison<void>(any const& lhs, any const& rhs) {
    return lhs.type() == typeid(void) && rhs.type() == typeid(void);
}

template <>
bool _simple_any_comparison<char const*>(any const& lhs, any const& rhs) {
    return lhs.type() == typeid(char const*) && rhs.type() == typeid(char const*) &&
           !strcmp(any_cast<char const*>(lhs), any_cast<char const*>(rhs));
}

void SerializableObject::Writer::_build_dispatch_tables() {
    /*
     * These are basically atomic writes to the encoder:
     */
    auto& wt = _write_dispatch_table;
    wt[&typeid(void)] = [this](any const&) { _encoder.write_null_value(); };
    wt[&typeid(bool)] = [this](any const& value) { _encoder.write_value(any_cast<bool>(value)); };
    wt[&typeid(int)] = [this](any const& value) { _encoder.write_value(any_cast<int>(value)); };
    wt[&typeid(int64_t)] = [this](any const& value) { _encoder.write_value(any_cast<int64_t>(value)); };
    wt[&typeid(double)] = [this](any const& value) { _encoder.write_value(any_cast<double>(value)); };
    wt[&typeid(std::string)] = [this](any const& value) { _encoder.write_value(any_cast<std::string const&>(value)); };
    wt[&typeid(char const*)] = [this](any const& value) {
        _encoder.write_value(std::string(any_cast<char const*>(value))); };
    wt[&typeid(RationalTime)] = [this](any const& value) { _encoder.write_value(any_cast<RationalTime const&>(value)); };
    wt[&typeid(TimeRange)] = [this](any const& value) { _encoder.write_value(any_cast<TimeRange const&>(value)); };
    wt[&typeid(TimeTransform)] = [this](any const& value) { _encoder.write_value(any_cast<TimeTransform const&>(value)); };

    /*
     * These next recurse back through the Writer itself:
     */
    wt[&typeid(SerializableObject::Retainer<>)] = [this](any const& value) {
        this->write(_no_key, any_cast<SerializableObject::Retainer<>>(value).value); };

    wt[&typeid(AnyDictionary)] = [this](any const& value) {
        this->write(_no_key, any_cast<AnyDictionary const&>(value)); };

    wt[&typeid(AnyVector)] = [this](any const& value) {
        this->write(_no_key, any_cast<AnyVector const&>(value)); };

    /*
     * Install a backup table, using the actual type name as a key.
     * This is to deal with type aliasing across compilation units.
     */
    for (auto e: wt) {
        _write_dispatch_table_by_name[e.first->name()] = e.second;
    }

    auto& et = _equality_dispatch_table;
    et[&typeid(void)] = &_simple_any_comparison<void>;
    et[&typeid(bool)] = &_simple_any_comparison<bool>;
    et[&typeid(int)] = &_simple_any_comparison<int>;
    et[&typeid(int64_t)] = &_simple_any_comparison<int64_t>;
    et[&typeid(double)] = &_simple_any_comparison<double>;
    et[&typeid(std::string)] = &_simple_any_comparison<std::string>;
    et[&typeid(char const*)] = &_simple_any_comparison<char const*>;
    et[&typeid(RationalTime)] = &_simple_any_comparison<RationalTime>;
    et[&typeid(TimeRange)] = &_simple_any_comparison<TimeRange>;
    et[&typeid(TimeTransform)] = &_simple_any_comparison<TimeTransform>;
    et[&typeid(SerializableObject::ReferenceId)] = &_simple_any_comparison<SerializableObject::ReferenceId>;

    /*
     * These next recurse back through the Writer itself:
     */
    et[&typeid(AnyDictionary)] = [this](any const& lhs, any const& rhs) { return _any_dict_equals(lhs, rhs); };
    et[&typeid(AnyVector)] = [this](any const& lhs, any const& rhs) { return _any_array_equals(lhs, rhs); };

}

bool SerializableObject::Writer::_any_dict_equals(any const& lhs, any const& rhs) {
    if (lhs.type() != typeid(AnyDictionary) || rhs.type() != typeid(AnyDictionary)) {
        return false;
    }

    AnyDictionary const& ld = any_cast<AnyDictionary const&>(lhs);
    AnyDictionary const& rd = any_cast<AnyDictionary const&>(rhs);

    auto r_it = rd.begin();

    for (auto l_it : ld) {
        if (r_it == rd.end()) {
            return false;
        }

        if (l_it.first != r_it->first || !_any_equals(l_it.second, r_it->second)) {
            return false;
        }
        ++r_it;
    }
    return r_it == rd.end();
}

bool SerializableObject::Writer::_any_array_equals(any const& lhs, any const& rhs) {
    if (lhs.type() != typeid(AnyVector) || rhs.type() != typeid(AnyVector)) {
        return false;
    }

    AnyVector const& lv = any_cast<AnyVector const&>(lhs);
    AnyVector const& rv = any_cast<AnyVector const&>(rhs);

    if (lv.size() != rv.size()) {
        return false;
    }

    for (size_t i = 0; i < lv.size(); i++) {
        if (!_any_equals(lv[i], rv[i])) {
            return false;
        }
    }

    return true;
}

bool SerializableObject::Writer::_any_equals(any const& lhs, any const& rhs) {
    auto e = _equality_dispatch_table.find(&lhs.type());
    return (e != _equality_dispatch_table.end()) && e->second(lhs, rhs);
}

bool SerializableObject::Writer::write_root(any const& value, Encoder& encoder, ErrorStatus* error_status) {
    Writer w(encoder);
    w.write(w._no_key, value);
    return !encoder.has_errored(error_status);
}

void SerializableObject::Writer::_encoder_write_key(std::string const& key) {
    if (&key != &_no_key) {
        _encoder.write_key(key);
    }
}

void SerializableObject::Writer::write(std::string const& key, bool value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, int value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, double value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, std::string const& value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, RationalTime value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, TimeRange value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, optional<RationalTime> value) {
    _encoder_write_key(key);
    value ? _encoder.write_value(*value) : _encoder.write_null_value();
}

void SerializableObject::Writer::write(std::string const& key, optional<TimeRange> value) {
    _encoder_write_key(key);
    value ? _encoder.write_value(*value) : _encoder.write_null_value();
}

void SerializableObject::Writer::write(std::string const& key, TimeTransform value) {
    _encoder_write_key(key);
    _encoder.write_value(value);
}

void SerializableObject::Writer::write(std::string const& key, SerializableObject const* value) {
    _encoder_write_key(key);
    if (!value) {
        _encoder.write_null_value();
        return;
    }

#ifdef OTIO_INSTANCING_SUPPORT
    auto e = _id_for_object.find(value);
    if (e != _id_for_object.end()) {
        /*
         * We've already written this value.
         */
        _encoder.write_value(SerializableObject::ReferenceId { e->second });
        return;
    }
#endif

    std::string const& schema_type_name = value->_schema_name_for_reference();
    if (_next_id_for_type.find(schema_type_name) == _next_id_for_type.end()) {
        _next_id_for_type[schema_type_name] = 0;
    }

    std::string next_id = schema_type_name + "-" + std::to_string(++_next_id_for_type[schema_type_name]);
    _id_for_object[value] = next_id;

    _encoder.start_object();

    _encoder.write_key("OTIO_SCHEMA");
    
    if (UnknownSchema const* us = dynamic_cast<UnknownSchema const*>(value)) {
        _encoder.write_value(string_printf("%s.%d", us->_original_schema_name.c_str(), us->_original_schema_version));
    }
    else {
        _encoder.write_value(string_printf("%s.%d", value->schema_name().c_str(), value->schema_version()));
    }

#ifdef OTIO_INSTANCING_SUPPORT
    _encoder.write_key("OTIO_REF_ID");
    _encoder.write_value(next_id);
#endif

    value->write_to(*this);

    _encoder.end_object();
}

void SerializableObject::Writer::write(std::string const& key, AnyDictionary const& value) {
    _encoder_write_key(key);

    _encoder.start_object();

    for (auto e: value) {
        write(e.first, e.second);
    }

    _encoder.end_object();
}

void SerializableObject::Writer::write(std::string const& key, AnyVector const& value) {
    _encoder_write_key(key);

    _encoder.start_array(value.size());

    for (auto e: value) {
        write(_no_key, e);
    }

    _encoder.end_array();
}

void SerializableObject::Writer::write(std::string const& key, any const& value) {
    std::type_info const& type = value.type();

    _encoder_write_key(key);

    auto e = _write_dispatch_table.find(&type);
    if (e == _write_dispatch_table.end()) {
        /*
         * Using the address of a type_info suffers from aliasing across compilation units.
         * If we fail on a lookup, we fallback on the by_name table, but that's slow because
         * we have to keep making a string each time.
         *
         * So when we fail, we insert the address of the type_info that failed to be found,
         * so that we'll catch it the next time.  This ensures we fail exactly once per alias
         * per type while using this writer.
         */
        auto backup_e = _write_dispatch_table_by_name.find(type.name());
        if (backup_e != _write_dispatch_table_by_name.end()) {
            _write_dispatch_table[&type] = backup_e->second;
            e = _write_dispatch_table.find(&type);
        }
    }

    if (e != _write_dispatch_table.end()) {
        e->second(value);
    }
    else {
        std::string s;
        std::string bad_type_name = (type == typeid(UnknownType)) ?
                                     demangled_type_name(any_cast<UnknownType>(value).type_name) :
                                     demangled_type_name(type);
            
        if (&key != &_no_key) {
            s = string_printf("Encountered object of unknown type '%s' under key '%s'",
                              bad_type_name.c_str(), key.c_str());
        }
        else {
            s = string_printf("Encountered object of unknown type '%s'",
                              bad_type_name.c_str());
        }

        _encoder._error(ErrorStatus(ErrorStatus::TYPE_MISMATCH, s));
        _encoder.write_null_value();
    }
}

bool SerializableObject::is_equivalent_to(SerializableObject const& other) const {
    if (_type_record() != other._type_record()) {
        return false;
    }

    CloningEncoder e1(false), e2(false);
    SerializableObject::Writer w1(e1);
    SerializableObject::Writer w2(e2);

    w1.write(w1._no_key, any(Retainer<>(this)));
    w2.write(w2._no_key, any(Retainer<>(&other)));

    return (!e1.has_errored() 
            && !e2.has_errored()
            && w1._any_equals(e1._root, e2._root));
}

SerializableObject* SerializableObject::clone(ErrorStatus* error_status) const {
    CloningEncoder e(true /* actually_clone*/);
    SerializableObject::Writer w(e);

    w.write(w._no_key, any(Retainer<>(this)));
    if (e.has_errored(error_status)) {
        return nullptr;
    }

    std::function<void (ErrorStatus const&)> error_function = 
        [error_status](ErrorStatus const& status) {
            *error_status = status;
    };


    e._resolver.finalize(error_function);

    return e._root.type() == typeid(SerializableObject::Retainer<>) ?
        any_cast<SerializableObject::Retainer<>&>(e._root).take_value() : nullptr;
}

std::string serialize_json_to_string(any const& value, ErrorStatus* error_status, int indent) {
    OTIO_rapidjson::StringBuffer s;    
    
    if (indent < 0) {
        OTIO_rapidjson::Writer<decltype(s)> json_writer(s);
        JSONEncoder<decltype(json_writer)> json_encoder(json_writer);

        if (!SerializableObject::Writer::write_root(value, json_encoder, error_status)) {
            return std::string();
        }
    }
    else {
        OTIO_rapidjson::PrettyWriter<decltype(s)> json_writer(s);
        JSONEncoder<decltype(json_writer)> json_encoder(json_writer);

        json_writer.SetIndent(' ', indent);
        if (!SerializableObject::Writer::write_root(value, json_encoder, error_status)) {
            return std::string();
        }
    }

    return std::string(s.GetString());
}

bool serialize_json_to_file(any const& value, std::string const& file_name,
                            ErrorStatus* error_status, int indent) {
    std::ofstream os(file_name);
    if (!os.is_open()) {
        *error_status = ErrorStatus(ErrorStatus::FILE_WRITE_FAILED, file_name);
        return false;
    }

    OTIO_rapidjson::OStreamWrapper osw(os);
    bool status;
    
    if (indent < 0) {
        OTIO_rapidjson::Writer<decltype(osw)> json_writer(osw);
        JSONEncoder<decltype(json_writer)> json_encoder(json_writer);
        status = SerializableObject::Writer::write_root(value, json_encoder, error_status);
    }
    else {
        OTIO_rapidjson::PrettyWriter<decltype(osw)> json_writer(osw);
        JSONEncoder<decltype(json_writer)> json_encoder(json_writer);

        json_writer.SetIndent(' ', indent);
        status = SerializableObject::Writer::write_root(value, json_encoder, error_status);
    }

    return status;
}

} }
