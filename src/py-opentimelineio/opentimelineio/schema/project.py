from .. import core


@core.register_type
class Project(core.SerializableObjectWithMetadata):
    _serializable_label = "Project.1"
    _name = 'Project'

    def __init__(self, name="", metadata=None):
        core.SerializableObjectWithMetadata.__init__(self, name, metadata)

        self.name = name

        self.collections = []
        self.timelines = []

        self.viewer_rate = None
        self.viewer_resolution = [None, None]
        self.viewer_lut = None

        if metadata:
            self.metadata.update(metadata)

        # Example of a quite common meta attribute
        self.metadata['OCIO_PATH'] = None

    timelines = core.serializable_field(
        "timelines",
        list,
        "collection of timelines"
    )

    collections = core.serializable_field(
        "collections",
        list,
        "collection of bins"
    )

    viewer_rate = core.serializable_field(
        "viewer_rate",
        float,
        "viewer playback rate"
    )

    viewer_resolution = core.serializable_field(
        "viewer_resolution",
        list,
        "viewer resolution"
    )

    viewer_lut = core.serializable_field(
        "viewer_lut",
        str,
        "viewer LUT"
    )

    def __repr__(self):
        return (
            'otio.schema.Project('
            'name={}, '
            'viewer_rate={}, '
            'viewer_resolution={}, '
            'viewer_lut={}, '
            'collections={}, '
            'timelines={}, '
            'metadata={}'
            ')'.format(
                repr(self.name),
                repr(self.viewer_rate),
                repr(self.viewer_resolution),
                repr(self.viewer_lut),
                repr(self.collections),
                repr(self.timelines),
                repr(self.metadata),
            )
        )
