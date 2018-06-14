from xml.dom import minidom
from xml.etree import cElementTree as et

import opentimelineio as otio


# Holders of elements
_producers = []
_playlists = []
_tracks = []


def _pretty_print_xml(root_e):
    tree = minidom.parseString(et.tostring(root_e, 'utf-8'))

    return tree.toprettyxml(indent="    ")


def _create_property(name, value=None):
    property_e = et.Element('property', name=name)
    if value is not None:
        property_e.text = str(value)

    return property_e


def _create_playlist(id):
    return et.Element('playlist', id=id)  # lint:ok


def _producer_lookup(_hash):
    for p in iter(_producers):
        if p.attrib['id'] == _hash:
            return p

    return None


def _create_producer(otio_item):
    a_range = otio_item.available_range()

    _in = str(a_range.start_time.value)
    _out = str(a_range.start_time.value + a_range.duration.value - 1)

    url = otio_item.media_reference.target_url
    # Some adapters store target_url as, well an url but MLT doesn't like it.
    if 'localhost' in url:
        url = url.replace('localhost', '')

    _hash = repr(hash(url))

    producer_e = _producer_lookup(_hash)

    if producer_e is not None:
        return producer_e

    producer_e = et.Element(
                        'producer',
                        id=_hash,  # lint:ok
                        **{
                            'in': _in,
                            'out': _out
                            }
                        )

    producer_e.append(_create_property('resource', url))

    # TODO: Check if oito_item has audio and apply a property for that
    # a_property_e = _create_property('audio_track', num_audio_tracks)
    # prducer_e.append(a_property_e)

    _producers.append(producer_e)

    return producer_e


def _create_entry(producer_id, clip_item):
    source_range = clip_item.source_range
    if isinstance(clip_item.media_reference, otio.schema.ExternalReference):
        available_range = clip_item.available_range()

    else:
        available_range = source_range

    inpoint = available_range.start_time.value - source_range.start_time.value
    entry_data = {
        'producer': producer_id,
        'in': str(inpoint),
        'out': str(inpoint + source_range.duration.value - 1)
        }
    entry_e = et.Element(
                    'entry',
                    **entry_data
                    )

    return entry_e


def _create_blank(otio_item):
    return et.Element('blank', length=str(otio_item.duration().value))


def write_to_string(input_otio):
    for tracknum, track in enumerate(input_otio.tracks):
        # TODO Figure out how to handle audio tracks
        if track.kind == otio.schema.TrackKind.Audio:
            continue

        playlist_e = _create_playlist(
                                id=track.name or 'V{n}'.format(n=tracknum + 1)
                                )

        for clip_item in track:
            if isinstance(clip_item, otio.schema.Clip):
                media_reference = clip_item.media_reference
                if isinstance(media_reference, otio.schema.ExternalReference):
                    producer_e = _create_producer(clip_item)
                    entry_e = _create_entry(producer_e.attrib['id'], clip_item)
                    playlist_e.append(entry_e)

                else:
                    blank_e = _create_blank(clip_item)
                    playlist_e.append(blank_e)

            elif isinstance(clip_item, otio.schema.Gap):
                blank_e = _create_blank(clip_item)
                playlist_e.append(blank_e)

        _playlists.append(playlist_e)
        track_e = et.Element('track', producer=playlist_e.get('id'))
        _tracks.append(track_e)

    root_e = et.Element('mlt')
    if 'resolution' in input_otio.metadata:
        root_e.attrib.update(input_otio.metadata['resolution'])

    root_e.extend(_producers)
    root_e.extend(_playlists)
    tractor_e = et.SubElement(root_e, 'tractor', id='tractor0')
    multitrack_e = et.SubElement(tractor_e, 'multitrack')
    multitrack_e.extend(_tracks)

    return _pretty_print_xml(root_e)
