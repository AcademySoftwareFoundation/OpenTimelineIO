package io.opentimeline;

import java.io.*;
import java.net.URL;

public class LibraryLoader {
    private static boolean libLoaded = false;

    public static String getExt() {
        String osName = System.getProperty("os.name");
        if (osName.equals("Linux"))
            return "so";
        else if (osName.equals("Mac OS X"))
            return "dylib";
        else
            return "dll";
    }

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
