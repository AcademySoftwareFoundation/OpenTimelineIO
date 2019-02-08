//
//  MetadataDictionary.swift
//
//  Created by David Baraff on 1/31/19.
//

import Foundation

public class MetadataDictionary {
    let mutationStamp: CxxAnyDictionaryMutationStamp
    
    public init() {
        self.mutationStamp = CxxAnyDictionaryMutationStamp()
    }
    
    init(anyDictionaryPtr: UnsafeMutableRawPointer) {
        self.mutationStamp = CxxAnyDictionaryMutationStamp(anyDictionaryPtr)
    }
    
}
