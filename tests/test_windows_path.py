
import unittest
import os
import sys

try:
    # Python 2.7
    import urlparse
    import urllib
except ImportError:
    # Python 3
    import urllib.parse as urlparse
    from urllib import request as urllib

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


class file_bundle_utils:
    @staticmethod
    def url_from_filepath(fpath):
        """convert a filesystem path to an url in a portable way using / path sep"""

        try:
            # appears to handle windows paths better, which are absolute and start
            # with a drive letter.
            return urlparse.unquote(pathlib.Path(fpath).as_uri())
        except ValueError:
            # scheme is "file" for absolute paths, else ""
            scheme = "file" if os.path.isabs(fpath) else ""

            # handles relative paths
            return urlparse.urlunparse(
                urlparse.ParseResult(
                    scheme=scheme,
                    path=fpath,
                    netloc="",
                    params="",
                    query="",
                    fragment=""
                )
            )

    @staticmethod
    def filepath_from_url(urlstr):
        """ Take a url and return a filepath """
        parsed_result = urlparse.urlparse(urlstr)
        return urllib.url2pathname(parsed_result.path)



SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
MEDIA_EXAMPLE_PATH_REL = os.path.relpath(
    os.path.join(
        os.path.dirname(__file__),
        "..",  # root
        "docs",
        "_static",
        "OpenTimelineIO@3xDark.png"
    )
)
MEDIA_EXAMPLE_PATH_URL_REL = file_bundle_utils.url_from_filepath(
    MEDIA_EXAMPLE_PATH_REL
)
MEDIA_EXAMPLE_PATH_ABS = os.path.abspath(
    MEDIA_EXAMPLE_PATH_REL.replace(
        "3xDark",
        "3xLight"
    )
)
MEDIA_EXAMPLE_PATH_URL_ABS = file_bundle_utils.url_from_filepath(
    MEDIA_EXAMPLE_PATH_ABS
)
# MEDIA_EXAMPLE_PATH_ABS = "D:/a/OpenTimelineIO/OpenTimelineIO/docs/_static/OpenTimelineIO@3xLight.png"
# MEDIA_EXAMPLE_PATH_URL_ABS = "file:///D:/a/OpenTimelineIO/OpenTimelineIO/docs/_static/OpenTimelineIO@3xLight.png"
#


class TestWindows(unittest.TestCase):
    def test_pathing(self):
        sys.stderr.write(
            "MEDIA_EXAMPLE_PATH_URL_ABS: {}\n".format(
                MEDIA_EXAMPLE_PATH_URL_ABS
            )
        )
        if sys.platform == "windows":
            self.assertEqual(MEDIA_EXAMPLE_PATH_URL_ABS.count("D:"), 1)
        self.assertTrue(MEDIA_EXAMPLE_PATH_URL_ABS.startswith("file://"))
        full_path = os.path.abspath(
            file_bundle_utils.filepath_from_url(MEDIA_EXAMPLE_PATH_URL_ABS)
        )
        if sys.platform == "windows":
            self.assertEqual(full_path.count("D:"), 1)
        else:
            self.assertNotIn("D:", full_path)

        # should have reconstructed it by this point
        self.assertEqual(full_path, MEDIA_EXAMPLE_PATH_ABS)


if __name__ == "__main__":
    unittest.main()
