# Stream and Channel Mapping

## Overview

OTIO's stream and channel mapping support allows media references to describe the individual streams they contain (video eyes, audio channels, etc.) and for timeline items to select or remix those streams via effects. The system has three layers: **addressing** a stream within a container, **describing** a stream's semantic role, and **selecting or mixing** streams on a clip.

---

## Layer 1: Addressing a Stream Within a Container

A `StreamAddress` identifies where a specific stream lives inside a media file. The appropriate `StreamAddress` subclass depends on how the container format identifies its streams. The `StreamAddress` subclass should be chosen based on how closely it matches the container's native identification scheme.

| Class | Use when |
|---|---|
| `IndexStreamAddress` | The container uses a single integer index per stream (e.g. WAV channel index, ffmpeg stream index) |
| `StreamChannelIndexStreamAddress` | The container organises media into tracks, each with one or more channels (e.g. MP4/MOV, MXF) |
| `StringStreamAddress` | The container uses string identifiers (e.g. codec name, channel label, USD scene path) |

### Format reference

Below is a chart of well-known media formats and the recommended `StreamAddress` subclass usage for each.

| Format | StreamAddress class | Notes                                                                                      |
|---|---|--------------------------------------------------------------------------------------------|
| WAV | `IndexStreamAddress` |                                                                                            |
| AIFF | `IndexStreamAddress` |                                                                                            |
| MOV / MP4 | `StreamChannelIndexStreamAddress` | When there is only one channel in a track (e.g. single-view video), use `channel_index=0`. |
| USD | `StringStreamAddress` | Use the USD path.                                                                          |
| PNG, JPEG, TIFF, GIF | *(single-image formats — no stream address needed)* |                                                                                            |

The above is not an exhaustive list. If you are working with a format not listed here, consider how its streams are identified and choose the `StreamAddress` subclass that best matches that scheme.

### StreamAddress

`StreamAddress` is the base class for all stream address types. You will not instantiate it directly; use one of the concrete subclasses below.

### IndexStreamAddress

Addresses a stream by a single integer index. Use for formats where each stream is identified by a flat index (e.g. a WAV file's channel index).

```python
# Stream 2 of a WAV file
addr = otio.schema.IndexStreamAddress(index=2)
```

### StreamChannelIndexStreamAddress

Addresses a stream by a track index and a channel index within that track. Use for container formats that organise media into named or numbered tracks, each potentially containing multiple channels (MOV, MP4).

```python
# Stream 1, channel 2 of an MP4
addr = otio.schema.StreamChannelIndexStreamAddress(stream_index=1, channel_index=2)
```

When a track contains only one channel (e.g. a single-view video track), use `channel_index=0`.

### StringStreamAddress

Addresses a stream by a string label or path. Use for formats where streams are identified by name rather than numeric index (e.g. a USD scene path, a codec channel label).

```python
# A camera in a USD scene
addr = otio.schema.StringStreamAddress(address="/World/set/cam_left")
```

---

## Layer 2: Describing a Stream's Semantic Role

Once you can locate a stream, the next layer describes what that stream *is* — its media kind, human-readable name, and semantic role. This information lives on the media reference and is keyed by well-known identifier strings.

### StreamInfo

`StreamInfo` describes a single media stream within a source. It is the smallest unit of temporal media — one eye's video, one audio channel, one camera view.

**Fields:**

- **`name`** — Human-readable label for this stream. May be any descriptive string (e.g. `"Alice lavalier (boom backup)"`, `"left eye"`). Not a semantic identifier.
- **`address`** — A `StreamAddress` subclass locating the stream in its container.
- **`kind`** — The type of media. Favor constants from `otio.schema.TrackKind` wherever appropriate.
- **`metadata`** — Arbitrary metadata dictionary for additional properties (e.g. ITU-R channel labels).

```python
stream = otio.schema.StreamInfo(
    name="Low Frequency Effects",
    address=otio.schema.StreamChannelIndexStreamAddress(stream_index=1, channel_index=3),
    kind=otio.schema.TrackKind.Audio,
    metadata={
        "ITU_label": "LFE",
    },
)
```

### StreamInfo.Identifier

`StreamInfo.Identifier` provides well-known strings that identify the **semantic role** of a stream — what presentation device it targets. These constants are the canonical keys for `available_streams`.

`otio.schema.StreamIdentifier` is an alias for `StreamInfo.Identifier`.

#### Visual streams

| Constant | Meaning |
|---|---|
| `monocular` | A traditional 2D video stream (single-view) |
| `left_eye` | Left eye in a stereo 3D pair |
| `right_eye` | Right eye in a stereo 3D pair |

#### Simple aural streams

| Constant | Meaning |
|---|---|
| `monaural` | Single mono audio channel |
| `stereo_left` | Left channel of a stereo pair |
| `stereo_right` | Right channel of a stereo pair |

> **Note:** Stereo and surround channels are kept separate because presenting the left/right channels of a surround mix as stereo is generally not a desirable result.

#### Surround aural streams (loosely based on ITU-R BS.2051-3)

| Constant | ITU label |
|---|---|
| `surround_left_front` | L |
| `surround_right_front` | R |
| `surround_center_front` | C |
| `surround_low_frequency_effects` | LFE |
| `surround_left_rear` | Ls |
| `surround_right_rear` | Rs |

### MediaReference.available_streams

`available_streams()` returns a dict keyed by stream identifier string mapping to `StreamInfo` objects. Use `set_available_streams()` to populate it.

#### Key conventions

1. **Presentation-ready streams** SHOULD use an `Identifier` constant directly as the key. This signals to consumers which stream serves a well-known role.

   ```python
   ref.set_available_streams({
       StreamInfo.Identifier.monocular: otio.schema.StreamInfo(
           name="main camera",
           address=otio.schema.IndexStreamAddress(index=0),
           kind=otio.schema.TrackKind.Video,
       ),
       StreamInfo.Identifier.stereo_left: otio.schema.StreamInfo(
           name="mix L",
           address=otio.schema.IndexStreamAddress(index=1),
           kind=otio.schema.TrackKind.Audio,
       ),
   })
   ```

2. **Additional streams** SHOULD prefix an `Identifier` value to form a unique key within the media reference.

   ```python
   # A music stem alongside the audio mix
   "music_stereo_left": otio.schema.StreamInfo(...)
   ```

3. **Arbitrary streams** MAY use any unique string when no well-known identifier applies — for example, spatial audio object IDs, or production audio tracks identified by mic placement.

   ```python
   "alice_lavalier": otio.schema.StreamInfo(...)
   ```

When generating these keys, try to avoid names that might collide with future `Identifier` constants unless you think your use case is in line with the precedent in that constant. In these cases, consider submitting a new constant to OTIO to include.

---

## Layer 3: Selecting or Mixing Streams on a Clip

Stream effects are `Effect` subclasses that attach to a clip's `effects` list and transform which streams are visible downstream and under what names. They operate on the stream identifiers declared in `available_streams`.

### StreamSelector

`StreamSelector` selects a subset of named streams from a clip and exposes them downstream with the **same names**. Use it to filter away streams you do not need without renaming them.

- **`output_streams`** — List of stream identifier strings to pass through. Values SHOULD be `Identifier` constants.

```python
# Select only the left eye from a stereo 3D clip
clip.effects.append(
    otio.schema.StreamSelector(
        output_streams=[StreamInfo.Identifier.left_eye]
    )
)

# Select a stereo pair from an 8 channel (5.1 + Stereo Mixdown) source
clip.effects.append(
    otio.schema.StreamSelector(
        output_streams=[
            StreamInfo.Identifier.stereo_left,
            StreamInfo.Identifier.stereo_right,
        ]
    )
)
```

### StreamMapper

`StreamMapper` renames stream identifiers as they pass through a clip. Each entry maps an **output** stream name (as it will appear downstream) to an **input** stream name (the key in the upstream `available_streams` map).

Use `StreamMapper` when a source uses one identifier but a downstream consumer expects a different one.

- **`stream_map`** — `{output_name: input_name}` dict. Keys and values SHOULD be `Identifier` constants where applicable.

```python
# Expose the left eye of a stereo source as the conventional monocular stream
clip.effects.append(
    otio.schema.StreamMapper(
        stream_map={
            StreamInfo.Identifier.monocular: StreamInfo.Identifier.left_eye
        }
    )
)
```

After this effect, downstream consumers that look up `StreamInfo.Identifier.monocular` would use the content addressed by the upstream `StreamInfo.Identifier.left_eye` entry.

### AudioMixMatrix

`AudioMixMatrix` mixes audio streams using a coefficient matrix. The structure is:

```
{ output_stream_name: { input_stream_name: coefficient, ... }, ... }
```

- **Output keys** SHOULD use `Identifier` constants where applicable. They correspond to the stream names that will appear in the downstream `available_streams` map after mixing.
- **Input keys** SHOULD match keys in the upstream `MediaReference.available_streams`.

```python
# Downmix 5.1 surround to Lo/Ro stereo
clip.effects.append(
    otio.schema.AudioMixMatrix(
        name="5.1_to_stereo",
        matrix={
            StreamInfo.Identifier.stereo_left: {
                StreamInfo.Identifier.surround_left_front:   1.0,
                StreamInfo.Identifier.surround_center_front: 0.707,
                StreamInfo.Identifier.surround_left_rear:    0.707,
            },
            StreamInfo.Identifier.stereo_right: {
                StreamInfo.Identifier.surround_right_front:  1.0,
                StreamInfo.Identifier.surround_center_front: 0.707,
                StreamInfo.Identifier.surround_right_rear:   0.707,
            },
        },
    )
)
```

### Comparison of Stream Effects

| Effect | Input | Output | Use when |
|---|---|---|---|
| `StreamSelector` | List of stream names to keep | Same streams, same names | You want to filter down to a subset of streams without renaming them |
| `StreamMapper` | `{output_name: input_name}` mapping | Renamed streams | A source uses one identifier but downstream expects a different name |
| `AudioMixMatrix` | `{output_name: {input_name: coefficient}}` matrix | New mixed streams | You need to combine or downmix audio channels with weighting |

These effects can be combined: for example, use `StreamSelector` to isolate a stereo pair from a source with 8-channel audio, then `AudioMixMatrix` on a downstream clip to downmix it further.

---

## Putting It Together

### Stereo 3D video clip + 5.1 audio downmix to stereo

This example models a more complex scenario: a single MOV file
containing stereo 3D video in stream 0 and a 5.1 surround audio mix in
stream 1. Two clips are built from the same reference — one that remaps the
left eye to monocular, and one that downmixes the surround channels to stereo.

```python
import opentimelineio as otio
from opentimelineio.schema import StreamInfo

# Single MOV reference.
# Stream 0: stereo 3D video (both eyes packed into one track, e.g. MV-HEVC or scalable AV1).
# Stream 1: 5.1 audio, six channels addressed by channel index.
ref = otio.schema.ExternalReference(target_url="/show/shot.mov")
ref.set_available_streams({
    # Video — stream 0. The Identifier distinguishes which eye to extract.
    StreamInfo.Identifier.left_eye: otio.schema.StreamInfo(
        name="left eye",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=0, channel_index=0
        ),
        kind=otio.schema.TrackKind.Video,
    ),
    StreamInfo.Identifier.right_eye: otio.schema.StreamInfo(
        name="right eye",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=0, channel_index=1
        ),
        kind=otio.schema.TrackKind.Video,
    ),
    # Audio — stream 1, one entry per surround channel.
    StreamInfo.Identifier.surround_left_front: otio.schema.StreamInfo(
        name="L",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=1, channel_index=0
        ),
        kind=otio.schema.TrackKind.Audio,
    ),
    StreamInfo.Identifier.surround_right_front: otio.schema.StreamInfo(
        name="R",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=1, channel_index=1
        ),
        kind=otio.schema.TrackKind.Audio,
    ),
    StreamInfo.Identifier.surround_center_front: otio.schema.StreamInfo(
        name="C",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=1, channel_index=2
        ),
        kind=otio.schema.TrackKind.Audio,
    ),
    StreamInfo.Identifier.surround_low_frequency_effects: otio.schema.StreamInfo(
        name="LFE",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=1, channel_index=3
        ),
        kind=otio.schema.TrackKind.Audio,
    ),
    StreamInfo.Identifier.surround_left_rear: otio.schema.StreamInfo(
        name="Ls",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=1, channel_index=4
        ),
        kind=otio.schema.TrackKind.Audio,
    ),
    StreamInfo.Identifier.surround_right_rear: otio.schema.StreamInfo(
        name="Rs",
        address=otio.schema.StreamChannelIndexStreamAddress(
            stream_index=1, channel_index=5
        ),
        kind=otio.schema.TrackKind.Audio,
    ),
})

# Video clip — remap left_eye to monocular for downstream consumers.
video_clip = otio.schema.Clip(name="shot_001_video", media_reference=ref)
video_clip.effects.append(
    otio.schema.StreamMapper(
        name="expose_left_eye_as_monocular",
        stream_map={
            StreamInfo.Identifier.monocular: StreamInfo.Identifier.left_eye,
        }
    )
)

# Audio clip — downmix 5.1 surround to Lo/Ro stereo.
audio_clip = otio.schema.Clip(name="shot_001_audio", media_reference=ref)
audio_clip.effects.append(
    otio.schema.AudioMixMatrix(
        name="5.1_to_stereo",
        matrix={
            StreamInfo.Identifier.stereo_left: {
                StreamInfo.Identifier.surround_left_front:            1.0,
                StreamInfo.Identifier.surround_center_front:          0.707,
                StreamInfo.Identifier.surround_left_rear:             0.707,
                StreamInfo.Identifier.surround_low_frequency_effects: 0.707,
            },
            StreamInfo.Identifier.stereo_right: {
                StreamInfo.Identifier.surround_right_front:           1.0,
                StreamInfo.Identifier.surround_center_front:          0.707,
                StreamInfo.Identifier.surround_right_rear:            0.707,
                StreamInfo.Identifier.surround_low_frequency_effects: 0.707,
            },
        },
    )
)
```
