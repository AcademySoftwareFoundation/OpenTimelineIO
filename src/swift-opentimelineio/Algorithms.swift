//
//  Algorithms.swift
//  otio_macos
//
//  Created by David Baraff on 4/2/19.
//

import Foundation

public enum Algorithms {
    static public func trackTrimmedToRange(track: Track, trimRange: TimeRange) throws -> Track {
        let result = try OTIOError.returnOrThrow { algorithms_track_trimmed_to_range(track, trimRange.cxxTimeRange, &$0) }
        return SerializableObject.findOrCreate(cxxPtr: result) as! Track
    }

    static public func flatten(stack: Stack) throws -> Track {
        let result = try OTIOError.returnOrThrow { algorithms_flatten_stack(stack, &$0) }
        return SerializableObject.findOrCreate(cxxPtr: result) as! Track
    }

    static public func flatten<ST : Sequence>(tracks: ST) throws -> Track where ST.Element == Track  {
        let result = try OTIOError.returnOrThrow { algorithms_flatten_track_array(tracks.map { $0 }, &$0) }
        return SerializableObject.findOrCreate(cxxPtr: result) as! Track
    }
}
