#include "opentimelineio/composable.h"
#include "opentimelineio/composition.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Composable::Composable(std::string const& name, AnyDictionary const& metadata)
    : Parent(name, metadata)
    , _parent(nullptr)
{}

Composable::~Composable()
{}

bool
Composable::visible() const
{
    return true;
}

bool
Composable::overlapping() const
{
    return false;
}

bool
Composable::_set_parent(Composition* new_parent) noexcept
{
    if (new_parent && _parent)
    {
        return false;
    }

    _parent = new_parent;
    return true;
}

Composable*
Composable::_highest_ancestor() noexcept
{
    Composable* c = this;
    for (; c->_parent; c = c->_parent)
    {
        /* empty */
    }
    return c;
}

bool
Composable::read_from(Reader& reader)
{
    return Parent::read_from(reader);
}

void
Composable::write_to(Writer& writer) const
{
    Parent::write_to(writer);
}

RationalTime
Composable::duration(ErrorStatus* error_status) const
{
    if (error_status)
    {
        *error_status = ErrorStatus::NOT_IMPLEMENTED;
    }
    return RationalTime();
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
