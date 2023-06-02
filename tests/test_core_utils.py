import copy
import unittest

import opentimelineio._otio
import opentimelineio.opentime
import opentimelineio.core._core_utils


class AnyDictionaryTests(unittest.TestCase):
    def test_main(self):
        opentimelineio.core._core_utils.AnyDictionary({
                'string': 'myvalue',
                'int': -999999999999,
                'list': [1, 2.5, 'asd'],
                'dict': {'map1': [345]},
                'AnyVector': opentimelineio.core._core_utils.AnyVector(),
                'AnyDictionary': opentimelineio.core._core_utils.AnyDictionary(),
                'RationalTime': opentimelineio.opentime.RationalTime(
                    value=10.0,
                    rate=5.0
                ),
                'TimeRange': opentimelineio.opentime.TimeRange(
                    opentimelineio.opentime.RationalTime(value=1.0),
                    opentimelineio.opentime.RationalTime(value=100.0)
                ),
                'TimeTransform': opentimelineio.opentime.TimeTransform(
                    offset=opentimelineio.opentime.RationalTime(value=55.0),
                    scale=999
                ),
                'SerializableObjectWithMetadata': opentimelineio._otio.SerializableObjectWithMetadata(),
            })

        d = opentimelineio.core._core_utils.AnyDictionary()
        d['a'] = 1

        self.assertTrue('a' in d)
        self.assertFalse('asdasdasd' in d)

        self.assertEqual(len(d), 1)
        self.assertEqual(d['a'], 1)  # New key

        with self.assertRaisesRegex(KeyError, "'non-existent'"):
            d['non-existent']

        # TODO: Test different type of values to exercise the any_to_py function?

        d['a'] = 'newvalue'
        self.assertEqual(d['a'], 'newvalue')

        self.assertTrue('a' in d)  # Test __contains__
        self.assertFalse('b' in d)

        with self.assertRaises(TypeError):
            d[1]  # AnyDictionary.__getitem__ only supports strings

        del d['a']
        self.assertEqual(dict(d), {})
        with self.assertRaisesRegex(KeyError, "'non-existent'"):
            del d['non-existent']

        for key in iter(d):  # Test AnyDictionaryProxy.Iterator.iter
            self.assertTrue(key)

        class CustomClass(object):
            pass

        with self.assertRaises(TypeError):
            d['custom'] = CustomClass()

        with self.assertRaises(ValueError):
            # Integer bigger than C++ int64_t can accept.
            d['super big int'] = 9223372036854775808

        with self.assertRaises(ValueError):
            # Integer smaller than C++ int64_t can accept.
            d['super big int'] = -9223372036854775809

    def test_raise_on_mutation_during_iter(self):
        d = opentimelineio.core._core_utils.AnyDictionary()
        d['a'] = 'test'
        d['b'] = 'asdasda'

        with self.assertRaisesRegex(ValueError, "container mutated during iteration"):
            for key in d:
                del d['b']

    def test_raises_if_ref_destroyed(self):
        d1 = opentimelineio.core._core_utils.AnyDictionary()
        opentimelineio._otio._testing.test_AnyDictionary_destroy(d1)

        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyDictionary has been destroyed"):  # noqa
            d1['asd']

        d2 = opentimelineio.core._core_utils.AnyDictionary()
        opentimelineio._otio._testing.test_AnyDictionary_destroy(d2)

        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyDictionary has been destroyed"):  # noqa
            d2['asd'] = 'asd'

        d3 = opentimelineio.core._core_utils.AnyDictionary()
        opentimelineio._otio._testing.test_AnyDictionary_destroy(d3)

        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyDictionary has been destroyed"):  # noqa
            del d3['asd']

        d4 = opentimelineio.core._core_utils.AnyDictionary()
        d4['asd'] = 1
        it = iter(d4)
        opentimelineio._otio._testing.test_AnyDictionary_destroy(d4)
        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyDictionary has been destroyed"):  # noqa
            next(it)


class AnyVectorTests(unittest.TestCase):
    def test_main(self):
        v = opentimelineio.core._core_utils.AnyVector()

        with self.assertRaises(IndexError):
            del v[0]  # There is a special case in the C++ code for empty vector

        v.append(1)
        self.assertEqual(len(v), 1)
        v.append(2)
        self.assertEqual(len(v), 2)

        self.assertEqual(v, [1, 2])

        v.insert(0, 5)
        self.assertEqual(v, [5, 1, 2])
        self.assertEqual(v[0], 5)
        self.assertEqual(v[-3], 5)

        with self.assertRaises(IndexError):
            v[100]

        with self.assertRaises(IndexError):
            v[-100]

        v[-1] = 100
        self.assertEqual(v[2], 100)

        with self.assertRaises(IndexError):
            v[-4] = -1

        with self.assertRaises(IndexError):
            v[100] = 100

        del v[0]
        self.assertEqual(len(v), 2)
        self.assertEqual(v, [1, 100])

        del v[1000]  # This will surprisingly delete the last item...
        self.assertEqual(len(v), 1)
        self.assertEqual(v, [1])

        # Will delete the last item even if the index doesn't match.
        # It's a surprising behavior.
        # This is caused by size_t(index)
        del v[-1000]

        v.extend([1, '234', {}])

        items = []
        for value in iter(v):  # Test AnyVector.Iterator.iter
            items.append(value)

        self.assertEqual(items, [1, '234', {}])
        self.assertTrue(v == [1, '234', {}])

        self.assertTrue(1 in v)  # Test __contains__
        self.assertTrue('234' in v)
        self.assertTrue({} in v)
        self.assertFalse(5 in v)

        self.assertEqual(list(reversed(v)), [{}, '234', 1])

        self.assertEqual(v.index('234'), 1)

        v += [1, 2]
        self.assertEqual(v.count(1), 2)

        self.assertEqual(v + ['new'], [1, '234', {}, 1, 2, 'new'])  # __add__
        self.assertEqual(['new'] + v, [1, '234', {}, 1, 2, 'new'])  # __radd__

        self.assertEqual(v + ('new',), [1, '234', {}, 1, 2, 'new'])  # noqa __add__ with non list type

        v2 = opentimelineio.core._core_utils.AnyVector()
        v2.append('v2')

        self.assertEqual(v + v2, [1, '234', {}, 1, 2, 'v2'])  # __add__ with AnyVector

        with self.assertRaises(TypeError):
            v + 'asd'  # __add__ invalid type

        self.assertEqual(str(v), "[1, '234', {}, 1, 2]")
        self.assertEqual(repr(v), "[1, '234', {}, 1, 2]")

        v3 = opentimelineio.core._core_utils.AnyVector()
        v3.extend(range(10))
        self.assertEqual(v3[2:], [2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(v3[4:8], [4, 5, 6, 7])
        self.assertEqual(v3[1:7:2], [1, 3, 5])

        del v3[2:7]
        self.assertEqual(v3, [0, 1, 7, 8, 9])

        v4 = opentimelineio.core._core_utils.AnyVector()
        v4.extend(range(10))

        del v4[::2]
        self.assertEqual(v4, [1, 3, 5, 7, 9])

        v5 = opentimelineio.core._core_utils.AnyVector()
        tmplist = [1, 2]
        v5.append(tmplist)
        # If AnyVector was a pure list, this would fail. But it's not a real list.
        # Appending copies data, completely removing references to it.
        self.assertIsNot(v5[0], tmplist)

    def test_raises_if_ref_destroyed(self):
        v1 = opentimelineio.core._core_utils.AnyVector()
        opentimelineio._otio._testing.test_AnyVector_destroy(v1)

        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyVector object has been destroyed"):  # noqa
            v1[0]

        v2 = opentimelineio.core._core_utils.AnyVector()
        opentimelineio._otio._testing.test_AnyVector_destroy(v2)

        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyVector object has been destroyed"):  # noqa
            v2[0] = 1

        v3 = opentimelineio.core._core_utils.AnyVector()
        opentimelineio._otio._testing.test_AnyVector_destroy(v3)

        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyVector object has been destroyed"):  # noqa
            del v3[0]

        v4 = opentimelineio.core._core_utils.AnyVector()
        v4.append(1)
        it = iter(v4)
        opentimelineio._otio._testing.test_AnyVector_destroy(v4)
        with self.assertRaisesRegex(ValueError, r"Underlying C\+\+ AnyVector object has been destroyed"):  # noqa
            next(it)

    def test_copy(self):
        list1 = [1, 2, [3, 4], 5]
        copied = copy.copy(list1)
        self.assertEqual(list1, copied)

        v = opentimelineio.core._core_utils.AnyVector()
        v.extend([1, 2, [3, 4], 5])

        copied = copy.copy(v)
        self.assertIsNot(v, copied)
        # AnyVector can only deep copy. So it's __copy__
        # does a deepcopy.
        self.assertIsNot(v[2], copied[2])

        deepcopied = copy.deepcopy(v)
        self.assertIsNot(v, deepcopied)
        self.assertIsNot(v[2], deepcopied[2])
