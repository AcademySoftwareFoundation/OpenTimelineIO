#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class GeneratorReference final : public MediaReference
{
public:
    struct Schema
    {
        static auto constexpr name   = "GeneratorReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    GeneratorReference(
        std::string const&         name            = std::string(),
        std::string const&         generator_kind  = std::string(),
        optional<TimeRange> const& available_range = nullopt,
        AnyDictionary const&       parameters      = AnyDictionary(),
        AnyDictionary const&       metadata        = AnyDictionary());

    std::string generator_kind() const noexcept { return _generator_kind; }

    void set_generator_kind(std::string const& generator_kind)
    {
        _generator_kind = generator_kind;
    }

    AnyDictionary& parameters() noexcept { return _parameters; }

    AnyDictionary parameters() const noexcept { return _parameters; }

protected:
    virtual ~GeneratorReference();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string   _generator_kind;
    AnyDictionary _parameters;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
