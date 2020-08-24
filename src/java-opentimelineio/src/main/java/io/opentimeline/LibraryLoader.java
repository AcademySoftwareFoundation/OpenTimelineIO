package io.opentimeline;

import java.io.IOException;

/**
 * This class uses NativeUtils to load native libraries from the JAR archive.
 * In case it is unable to load them from the JAR archive it falls back to try loading from the system.
 */
public class LibraryLoader {
    private static boolean libLoaded = false;

    public static void load(String name) {
        if (libLoaded)
            return;
        final String libname = System.mapLibraryName(name);
        final String opentimelibname = System.mapLibraryName("opentime");
        final String OTIOlibname = System.mapLibraryName("opentimelineio");
        final String libPkgPath = "/" + libname;
        final String libOpentimePath = "/" + opentimelibname;
        final String libOTIOPath = "/" + OTIOlibname;
        try {
            NativeUtils.loadLibraryFromJar(libOpentimePath);
            NativeUtils.loadLibraryFromJar(libOTIOPath);
            NativeUtils.loadLibraryFromJar(libPkgPath);
            libLoaded = true;
        } catch (IllegalArgumentException | IOException e) {
            System.loadLibrary("opentime");
            System.loadLibrary("opentimelineio");
            System.loadLibrary(name);
            libLoaded = true;
        } catch (Exception e) {
            libLoaded = false;
            System.err.println("Unable to load native library.");
        }
    }
}
