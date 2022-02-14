#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class MultiMediaReference final : public MediaReference
{
    using References = std::vector<Retainer<MediaReference>>;

public:
    struct Schema
    {
        static auto constexpr name   = "MultiMediaReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    MultiMediaReference(
        std::string const&   name     = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

    optional<TimeRange> available_range() const noexcept final;

    void set_available_range(optional<TimeRange> const& available_range) final;

protected:
    virtual ~MultiMediaReference();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    References _references;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
