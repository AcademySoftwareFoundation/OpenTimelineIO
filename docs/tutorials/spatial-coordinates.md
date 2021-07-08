# OTIO Spatial Coordinate System
This document describes a proposed coordinate system for OpenTimelineIO. It focuses mainly on the Bounds object, which is a rectangular area represented through a 2D box within that coordinate system.  

## Coordinate System
The proposed spatial coordinate system is unit-less.  
It allows decoupling clip layouts from pixel density.  
It has a single origin (X=0.0, Y=0.0) and is used as a unique canvas across the whole Timeline.  
Y-Axis-Up convention is used.  

![Coordinate System](../_static/spatial_coords_system.svg)
## Bounds

A Bounds object is a 2D box that defines a spatial area in the unit-less coordinate system.  
Here is an example of Bounds defining a first-quadrant-snapped rectangle with a width of 16 and a height of 9.  
Note that, since Bounds are serializable object, they have a metadata member.  
```
"bounds": {
  "OTIO_SCHEMA": "Bounds.1",
  "box": {
    "OTIO_SCHEMA": "Box2d.1",
    "min": {
      "OTIO_SCHEMA":"V2d.1",
      "x": 0.0,
      "y": 0.0
    },
    "max": {
      "OTIO_SCHEMA":"V2d.1",
      "x": 16.0,
      "y": 9.0
    }
  },
  "metadata": {}
}
```

![Example 1](../_static/spatial_coords_example1.svg)  

Here is another example of Bounds defining an origin-centered rectangle with a width of 16 and a height of 9.  
```
"bounds": {
  "OTIO_SCHEMA": "Bounds.1",
  "box": {
    "OTIO_SCHEMA": "Box2d.1",
    "min": {
      "OTIO_SCHEMA":"V2d.1",
      "x": -8.0,
      "y": -4.5
    },
    "max": {
      "OTIO_SCHEMA":"V2d.1",
      "x": 8.0,
      "y": 4.5
    }
  }
}
```

![Example 2](../_static/spatial_coords_example2.svg)

When multiple clips are being rendered, either through a transition or through the presence of a multi-tracks timeline, all clips share the same coordinate system.  

For instance, if we add an origin-centered square clip on top of the previous one, here is what we get.  

![Example 3](../_static/spatial_coords_example3.svg)  

Since each clip has its own bounds properties, clips can be arranged into complex layouts.  

This can be used in several contexts, for instance:  

-   Side-by-side comparison
-   Picture-In-Picture
-   Complex spatial layouts for notes (collage)

Example of a Picture-In-Picture layout added on top of the previous 2-clips layout:  
![Example 4](../_static/spatial_coords_example4.svg)  
## Bounds and Clips
Currently, we use the Bounds object at the ***Clip.media_reference.bounds*** level. This allows support for different bounds when changing the media-representation of a given Clip. For instance, a Clip could have 2 media-representations (a set of High-Res 16:9 OpenEXR files and a Low-Res 4:3 MP4 file). Those 2 media-representations might not cover the same spatial area, therefore it makes sense for them to have their individual Bounds region.  
## Non-Bounds representations
The coordinate system can also be used to describe non-rectangular coordinates. For instance, effects that have spatial-based parameters that need to be expressed in a resolution-independent way could use the same system.  

Examples of potential usage for this coordinate system:  

-   Blur amount
-   Annotation position
-   Wipe bar position (angular mask)

