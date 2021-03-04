
import unittest
import os
import sys

try:
    # Python 2.7
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


class file_bundle_utils:
    @staticmethod
    def file_url_of(fpath):
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
MEDIA_EXAMPLE_PATH_URL_REL = file_bundle_utils.file_url_of(
    MEDIA_EXAMPLE_PATH_REL
)
MEDIA_EXAMPLE_PATH_ABS = os.path.abspath(
    MEDIA_EXAMPLE_PATH_REL.replace(
        "3xDark",
        "3xLight"
    )
)
MEDIA_EXAMPLE_PATH_URL_ABS = file_bundle_utils.file_url_of(
    MEDIA_EXAMPLE_PATH_ABS
)


class TestWindows(unittest.TestCase):
    def test_pathing(self):
        sys.stderr.write(
            "MEDIA_EXAMPLE_PATH_URL_ABS: {}\n".format(
                MEDIA_EXAMPLE_PATH_URL_ABS
            )
        )
        self.assertEqual(MEDIA_EXAMPLE_PATH_URL_ABS.count("D:"), 1)

        # parse the url and check the result
        parsed_result = urlparse.urlparse(MEDIA_EXAMPLE_PATH_URL_ABS)
        sys.stderr.write(
            "parsed_result: {}\n".format(parsed_result)
        )
        full_path = os.path.abspath(parsed_result.path)
        sys.stderr.write(
            "full_path: {}\n".format(full_path)
        )
        self.assertEqual(full_path.count("D:"), 1)

        # should have reconstructed it by this point
        self.assertEqual(full_path, MEDIA_EXAMPLE_PATH_ABS)


if __name__ == "__main__":
    unittest.main()
