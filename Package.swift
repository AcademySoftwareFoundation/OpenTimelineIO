// swift-tools-version:5.3
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "OpenTimelineIO",
    platforms: [.macOS(.v10_13),
		.iOS(.v11)],
    products: [
        .library(name: "OpenTime_CXX", targets: ["OpenTime_CXX"]),
        .library(name: "OpenTimelineIO_CXX", targets: ["OpenTimelineIO_CXX"]),
        .library(name: "OpenTimelineIO", targets: ["OpenTimelineIO"])
    ],
    dependencies: [],
    targets: [
		// public target
        .target(name: "OpenTime_CXX",
			path: "src/opentime",
			exclude: ["CMakeLists.txt"], 
			sources: ["."],
			publicHeadersPath: ".",
			cxxSettings: [  .headerSearchPath("..")]
			),

		// public target
        .target(name: "OpenTimelineIO_CXX",
			dependencies: ["OpenTime_CXX"],
			path: "src/opentimelineio",
			exclude: ["main.cpp", "CMakeLists.txt"],
			sources: ["."],
			publicHeadersPath: ".",
			cxxSettings: [  .headerSearchPath("../deps/rapidjson/include"), 
							.headerSearchPath("../deps"), 
							.headerSearchPath("../deps/optional-lite/include"),
							.headerSearchPath("..")]
			),

		// private target
		.target(name: "OpenTimelineIO_objc",
			dependencies: ["OpenTimelineIO_CXX"],
			path: "src/swift-opentimelineio/Sources/objc",
			sources: ["."],
			publicHeadersPath: "include",
			cxxSettings: [  .headerSearchPath("../../../deps/rapidjson/include"), 
							.headerSearchPath("../../../deps"), 
							.headerSearchPath("../../../deps/optional-lite/include"),
							.headerSearchPath("../../.."),
							.headerSearchPath(".")]
			),

		// public target
		.target(name: "OpenTimelineIO",
			dependencies: ["OpenTimelineIO_objc"],
			path: "./src/swift-opentimelineio/Sources",
			exclude: ["objc"],
			sources: ["swift"]),

		.testTarget(name: "OpenTimelineIOTests",
			dependencies: ["OpenTimelineIO"],
			path: "./src/swift-opentimelineio/Tests/OpenTimelineIOTests",
			sources: ["."],
			resources: [.process("data")])

    ],
    cxxLanguageStandard: .cxx11
)
