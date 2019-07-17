from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.ExternalReference)
def __str__(self):
    return 'ExternalReference("{}")'.format(str(self.target_url))


@add_method(_otio.ExternalReference)
def __repr__(self):
    return 'otio.schema.ExternalReference(target_url={})'.format(
        repr(str(self.target_url))
    )
