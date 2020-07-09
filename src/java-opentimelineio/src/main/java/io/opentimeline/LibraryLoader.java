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
        String path = "/lib" + name + "." + getExt();
        URL url = cls.getResource(path);

        Boolean success = false;
        try {
            final File libfile = File.createTempFile(name, ".lib");
            libfile.deleteOnExit();

            final InputStream in = url.openStream();
            final OutputStream out = new BufferedOutputStream(new FileOutputStream(libfile));

            int len = 0;
            byte[] buffer = new byte[8192];
            while ((len = in.read(buffer)) > -1)
                out.write(buffer, 0, len);
            out.close();
            in.close();

            System.load(libfile.getAbsolutePath());
            success = true;
        } catch (IOException x) {

        }

        return success;
    }
}
