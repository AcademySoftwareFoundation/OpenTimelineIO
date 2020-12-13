import OpenTimelineIO

func main() {
    let sowm = SerializableObjectWithMetadata()
    let clip = Clip()

    sowm.metadata["anInt"] = 1
    sowm.metadata["aString"] = "foo"
    sowm.metadata["aVector"] = Metadata.Vector(arrayLiteral: 3, "abc", clip)
    sowm.name = "sowm"

    let sowm2 = try! sowm.clone() as! SerializableObjectWithMetadata
    assert(sowm2.isEquivalent(to: sowm))

    let sowm3 = SerializableObjectWithMetadata(name: sowm.name, metadata: sowm.metadata)
    let sowm4 = SerializableObjectWithMetadata(name: sowm3.name, metadata: sowm3.metadata.map { $0 })
    assert(sowm3.isEquivalent(to: sowm4))

    print(try! sowm.toJSON())
}

main()
