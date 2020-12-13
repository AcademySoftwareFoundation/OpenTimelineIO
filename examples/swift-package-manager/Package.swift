// swift-tools-version:5.1
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "otio_examples",
    platforms: [.macOS(.v10_13)],
    dependencies: [
	.package(url: "https://github.com/davidbaraff/OpenTimelineIO.git", .branch("spm"))
    ],
    targets: [
	.target(name: "cxx_opentime_example",
                dependencies: ["OpenTime_CXX"]),
	.target(name: "cxx_example",
                dependencies: ["OpenTimelineIO_CXX"]),
	.target(name: "swift_example",
                dependencies: ["OpenTimelineIO"])
    ],
    cxxLanguageStandard: CXXLanguageStandard.cxx11    
)
