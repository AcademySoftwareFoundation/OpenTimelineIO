__doc__ = """ Exception classes for OpenTimelineIO """

# base


class OTIOError(Exception):
    pass


class CouldNotReadFileError(OTIOError):
    pass


class NoKnownAdapterForExtensionError(OTIOError):
    pass


class ReadingNotSupportedError(OTIOError):
    pass


class WritingNotSupportedError(OTIOError):
    pass


class NotSupportedError(OTIOError):
    pass


class InvalidSerializeableLabelError(OTIOError):
    pass


class CannotComputeDurationError(OTIOError):
    pass


class AdapterDoesntSupportFunctionError(OTIOError):
    pass


class UnsupportedSchemaError(OTIOError):
    pass


class NotAChildError(OTIOError):
    pass
