#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

import unittest
import threading
import weakref

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class MultithreadingTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test1(self):
        self.sc = otio.schema.SerializableCollection()
        child = otio.core.SerializableObject()
        child.extra = 17
        wc = weakref.ref(child)
        self.assertEqual(wc() is not None, True)
        self.sc.append(child)
        del child

        threads = []
        for i in range(5):
            t = threading.Thread(target=self.bash_retainers1)
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.assertEqual(self.sc[0].extra, 17)
        self.sc.pop()
        self.assertEqual(wc() is None, True)

    def bash_retainers1(self):
        otio._otio._testing.bash_retainers1(self.sc)

    def test2(self):
        sc = otio.schema.SerializableCollection()
        child = otio.core.SerializableObject()
        sc.append(child)
        self.materialized = False

        self.sc = sc.clone()
        self.lock = threading.Lock()
        # self.sc[0] has not been given out to Python yet

        threads = []
        for i in range(5):
            t = threading.Thread(target=self.bash_retainers2)
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.assertEqual(self.wc() is not None, True)
        self.assertEqual(self.wc().extra, 37)
        del self.sc
        self.assertEqual(self.wc() is None, True)

    def test3(self):
        t = threading.Thread(target=self.gil_scoping)
        t.daemon = True
        t.start()
        t.join()

    def test4(self):
        self.gil_scoping()

    def gil_scoping(self):
        otio._otio._testing.gil_scoping()

    def materialize(self):
        with self.lock:
            if not self.materialized:
                self.materialized = True
                child = self.sc[0]
                self.wc = weakref.ref(child)
                self.assertEqual(self.wc() is not None, True)
                child.extra = 37
                del child

    def bash_retainers2(self):
        otio._otio._testing.bash_retainers2(self.sc, self.materialize)


if __name__ == '__main__':
    unittest.main()
