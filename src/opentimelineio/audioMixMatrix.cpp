// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/audioMixMatrix.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

AudioMixMatrix::AudioMixMatrix(
    std::string const&   name,
    std::string const&   effect_name,
    MixMatrix const&     matrix,
    AnyDictionary const& metadata)
    : Parent(name, effect_name, metadata)
    , _matrix(matrix)
{}

AudioMixMatrix::~AudioMixMatrix()
{}

bool
AudioMixMatrix::read_from(Reader& reader)
{
    return reader.read_if_present("matrix", &_matrix) && Parent::read_from(reader);
}

void
AudioMixMatrix::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("matrix", _matrix);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
