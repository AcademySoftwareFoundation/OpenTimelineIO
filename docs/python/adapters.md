# Adapters

While OpenTimelineIO favors the `.otio` JSON format, Python OpenTimelineIO supports many file formats via adapter plugins.

## Built-In Adapters

The OpenTimelineIO native file format adapters that are present in the `opentimelineio` python package are:

- [otio_json](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/src/py-opentimelineio/opentimelineio/adapters/otio_json.py) - OpenTimelineIO's native file format.
- [otiod](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/src/py-opentimelineio/opentimelineio/adapters/otiod.py) - a directory bundle of a `.otio` file along with referenced media.
- [otioz](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/src/py-opentimelineio/opentimelineio/adapters/otioz.py) - a zip file bundle of a `.otio` file along with referenced media.

## Batteries-Included Adapters

To also install a curated list of additional useful adapters, use the [OpenTimelineIO-Plugins ](https://pypi.org/project/OpenTimelineIO-Plugins/) python package. In addition to the OpenTimelineIO native adapters, you'll get aditional useful adapters including:

- [AAF](https://github.com/OpenTimelineIO/otio-aaf-adapter)
- [ale](https://github.com/OpenTimelineIO/otio-ale-adapter)
- [burnins](https://github.com/OpenTimelineIO/otio-burnins-adapter)
- [cmx_3600](https://github.com/OpenTimelineIO/otio-cmx3600-adapter)
- [fcp_xml](https://github.com/OpenTimelineIO/otio-fcp-adapter)
- [fcpx_xml](https://github.com/OpenTimelineIO/otio-fcpx-xml-adapter)
- [hls_playlist](https://github.com/OpenTimelineIO/otio-hls-playlist-adapter)
- [maya_sequencer](https://github.com/OpenTimelineIO/otio-maya-sequencer-adapter)
- [svg](https://github.com/OpenTimelineIO/otio-svg-adapter)
- [xges](https://github.com/OpenTimelineIO/otio-xges-adapter)

These adapters are supported by the broader OpenTimelineIO community. While the OTIO core team consults and sometimes contribute to their development, they may be maintained and supported at varying levels.

## Additional Adapters

Below are some other adapters that may be useful to some users:

- [kdenlive](https://invent.kde.org/multimedia/kdenlive-opentimelineio)

## Custom Adapters

Adapters are implemented as plugins for OpenTimelineIO and can either be registered via an [environment variable](./otio-env-variables) or by packaging in a Python module with a particular entrypoint defined. For more detail, see the [Writing an OTIO Adapter](/python-tutorials/write-an-adapter) tutorial.

