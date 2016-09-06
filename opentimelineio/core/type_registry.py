# Types decorate use register_type() to insert themselves into this map
_OTIO_TYPES = {}


def register_type(classobj):
    """ Register a class to a Schema Label.  """
    _OTIO_TYPES[classobj.serializeable_label] = classobj

    return classobj
