package io.opentimeline;

import java.io.*;
import java.net.URL;

public class LibraryLoader {
    public static String getExt() {
        String osName = System.getProperty("os.name");
        if (osName.equals("Linux"))
            return "so";
        else if (osName.equals("Mac OS X"))
            return "dylib";
        else
            return "dll";
    }

    public static Boolean load(Class<?> cls, String name) {
        final String libname = System.mapLibraryName(name);
        final String libPkgPath = "/lib/" + libname;
        final String libOpentimePath = "/lib/opentime";
        final String libOTIOPath = "/lib/opentimelineio";
        try {
            NativeUtils.loadLibraryFromJar(libOpentimePath);
            NativeUtils.loadLibraryFromJar(libOTIOPath);
            NativeUtils.loadLibraryFromJar(libPkgPath);
            return true;
        } catch (IllegalArgumentException | IOException e) {
            System.loadLibrary("opentime");
            System.loadLibrary("opentimelineio");
            System.loadLibrary(name);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
