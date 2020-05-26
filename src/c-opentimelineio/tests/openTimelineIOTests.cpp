#include "gtest/gtest.h"

#include <copentimelineio/anyDictionary.h>
#include <iostream>

class OpenTimelineIOTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() {}
};

TEST_F(OpenTimelineIOTests, AnyDictionaryTest)
{
    Any*                   a      = Any_create(1);
    Any*                   b      = Any_create(2);
    Any*                   c      = Any_create(3);
    AnyDictionary*         adict  = AnyDictionary_create();
    AnyDictionaryIterator* it1    = AnyDictionary_insert(adict, "any1", a);
    AnyDictionaryIterator* it2    = AnyDictionary_insert(adict, "any2", b);
    AnyDictionaryIterator* it3    = AnyDictionary_insert(adict, "any3", c);
    AnyDictionaryIterator* it     = AnyDictionary_begin(adict);
    AnyDictionaryIterator* it_end = AnyDictionary_end(adict);
    int                    count  = 0;
    for(; AnyDictionaryIterator_not_equal(it, it_end);
        AnyDictionaryIterator_advance(it, 1))
    {
        count++;
    }
    EXPECT_EQ(count, 3);
    Any_destroy(a);
    Any_destroy(b);
    Any_destroy(c);
    AnyDictionary_destroy(adict);
    AnyDictionaryIterator_destroy(it1);
    AnyDictionaryIterator_destroy(it2);
    AnyDictionaryIterator_destroy(it3);
    AnyDictionaryIterator_destroy(it);
    AnyDictionaryIterator_destroy(it_end);
    a = b = c = NULL;
    adict     = NULL;
    it1 = it2 = it3 = it = it_end = NULL;
}