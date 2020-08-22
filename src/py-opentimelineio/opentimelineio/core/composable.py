from . _core_utils import add_method
from .. import _otio


@add_method(_otio.Composable)
def __repr__(self):
    return (
        "otio.{}("
        "name={}, "
        "metadata={}"
        ")".format(
            "core.Composable",
            repr(str(self.name)),
            repr(self.metadata)
        )
    )


@add_method(_otio.Composable)
def __str__(self):
    return "{}({}, {})".format(
        "Composable",
        str(self.name),
        str(self.metadata)
    )
