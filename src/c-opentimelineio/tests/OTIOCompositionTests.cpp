#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <copentime/timeRange.h>
#include <copentimelineio/clip.h>
#include <copentimelineio/composable.h>
#include <copentimelineio/composableVector.h>
#include <copentimelineio/composition.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/item.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/stack.h>
#include <copentimelineio/track.h>
#include <copentimelineio/transition.h>
#include <iostream>

#define xstr(s) str(s)
#define str(s) #s

class OTIOCompositionTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

class OTIOStackTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

class OTIOTrackTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOCompositionTests, ConstructorTest)
{
    Item*             it = Item_create(NULL, NULL, NULL, NULL, NULL);
    Composition*      co = Composition_create("test", NULL, NULL, NULL, NULL);
    ComposableVector* composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) it);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool resultOK = Composition_set_children(co, composableVector, errorStatus);

    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) co),
        "test");

    EXPECT_STREQ(Composition_composition_kind(co), "Composition");

    ASSERT_TRUE(resultOK);

    ComposableRetainerVector* composableRetainerVector =
        Composition_children(co);

    ASSERT_EQ(
        ComposableVector_size(composableVector),
        ComposableRetainerVector_size(composableRetainerVector));

    ComposableRetainerVectorIterator* retainerIt =
        ComposableRetainerVector_begin(composableRetainerVector);
    ComposableRetainerVectorIterator* retainerItEnd =
        ComposableRetainerVector_end(composableRetainerVector);
    ComposableVectorIterator* vectorIt =
        ComposableVector_begin(composableVector);

    for(; ComposableRetainerVectorIterator_not_equal(retainerIt, retainerItEnd);
        ComposableRetainerVectorIterator_advance(retainerIt, 1),
        ComposableVectorIterator_advance(vectorIt, 1))
    {
        Composable* composableVectorElement =
            ComposableVectorIterator_value(vectorIt);
        RetainerComposable* retainerVectorElement =
            ComposableRetainerVectorIterator_value(retainerIt);
        Composable* retainerComposableValue =
            RetainerComposable_take_value(retainerVectorElement);

        ASSERT_TRUE(SerializableObject_is_equivalent_to(
            (SerializableObject*) composableVectorElement,
            (SerializableObject*) retainerComposableValue));

        RetainerComposable_managed_destroy(retainerVectorElement);
        retainerVectorElement = NULL;
        SerializableObject_possibly_delete(
            (SerializableObject*) composableVectorElement);
        composableVectorElement = NULL;
    }

    SerializableObject_possibly_delete((SerializableObject*) it);
    it = NULL;
    SerializableObject_possibly_delete((SerializableObject*) co);
    co = NULL;
    ComposableVector_destroy(composableVector);
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    ComposableRetainerVector_destroy(composableRetainerVector);
    composableRetainerVector = NULL;
    ComposableRetainerVectorIterator_destroy(retainerIt);
    retainerIt = NULL;
    ComposableRetainerVectorIterator_destroy(retainerItEnd);
    retainerItEnd = NULL;
    ComposableVectorIterator_destroy(vectorIt);
    vectorIt = NULL;
}

TEST_F(OTIOCompositionTests, EqualityTest)
{
    Composition* co0  = Composition_create(NULL, NULL, NULL, NULL, NULL);
    Composition* co00 = Composition_create(NULL, NULL, NULL, NULL, NULL);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) co0, (SerializableObject*) co00));

    Item*             a   = Item_create("A", NULL, NULL, NULL, NULL);
    Item*             b   = Item_create("B", NULL, NULL, NULL, NULL);
    Item*             c   = Item_create("C", NULL, NULL, NULL, NULL);
    Composition*      co1 = Composition_create(NULL, NULL, NULL, NULL, NULL);
    ComposableVector* composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) a);
    ComposableVector_push_back(composableVector, (Composable*) b);
    ComposableVector_push_back(composableVector, (Composable*) c);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    bool resultOK =
        Composition_set_children(co1, composableVector, errorStatus);
    ASSERT_TRUE(resultOK);
    ComposableVector_destroy(composableVector);
    composableVector = NULL;

    Item*        x   = Item_create("X", NULL, NULL, NULL, NULL);
    Item*        y   = Item_create("Y", NULL, NULL, NULL, NULL);
    Item*        z   = Item_create("Z", NULL, NULL, NULL, NULL);
    Composition* co2 = Composition_create(NULL, NULL, NULL, NULL, NULL);
    composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) x);
    ComposableVector_push_back(composableVector, (Composable*) y);
    ComposableVector_push_back(composableVector, (Composable*) z);
    resultOK = Composition_set_children(co2, composableVector, errorStatus);
    ASSERT_TRUE(resultOK);
    ComposableVector_destroy(composableVector);
    composableVector = NULL;

    Item*        a2  = Item_create("A", NULL, NULL, NULL, NULL);
    Item*        b2  = Item_create("B", NULL, NULL, NULL, NULL);
    Item*        c2  = Item_create("C", NULL, NULL, NULL, NULL);
    Composition* co3 = Composition_create(NULL, NULL, NULL, NULL, NULL);
    composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) a2);
    ComposableVector_push_back(composableVector, (Composable*) b2);
    ComposableVector_push_back(composableVector, (Composable*) c2);
    resultOK = Composition_set_children(co3, composableVector, errorStatus);
    ASSERT_TRUE(resultOK);
    ComposableVector_destroy(composableVector);
    composableVector = NULL;

    EXPECT_FALSE(SerializableObject_is_equivalent_to(
        (SerializableObject*) co1, (SerializableObject*) co2));
    /*EXPECT_TRUE(SerializableObject_is_equivalent_to( //TODO Fix Segfault
        (SerializableObject*) co1, (SerializableObject*) co3));*/

    //    SerializableObject_possibly_delete((SerializableObject*) co0);
    //    co0 = NULL;
    //    SerializableObject_possibly_delete((SerializableObject*) co00);
    //    co00 = NULL;
    //    SerializableObject_possibly_delete((SerializableObject*) co1);
    //    co1 = NULL;
    //    SerializableObject_possibly_delete((SerializableObject*) co2);
    //    co2 = NULL;
    SerializableObject_possibly_delete((SerializableObject*) co3);
    co3 = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}
TEST_F(OTIOCompositionTests, IsParentOfTest)
{
    Composition*     co   = Composition_create(NULL, NULL, NULL, NULL, NULL);
    Composition*     co_2 = Composition_create(NULL, NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    EXPECT_FALSE(Composition_is_parent_of(co, (Composable*) co_2));
    bool appendOK =
        Composition_append_child(co, (Composable*) co_2, errorStatus);
    EXPECT_TRUE(Composition_is_parent_of(co, (Composable*) co_2));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    SerializableObject_possibly_delete((SerializableObject*) co);
    co = NULL;
}

TEST_F(OTIOCompositionTests, ParentManipTest)
{
    Item*             it = Item_create(NULL, NULL, NULL, NULL, NULL);
    Composition*      co = Composition_create(NULL, NULL, NULL, NULL, NULL);
    ComposableVector* composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) it);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool resultOK = Composition_set_children(co, composableVector, errorStatus);
    Composition* parent = Composable_parent((Composable*) it);
    EXPECT_EQ(parent, co);

    SerializableObject_possibly_delete((SerializableObject*) co);
    co = NULL;
    ComposableVector_destroy(composableVector);
    composableVector = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOCompositionTests, MoveChildTest)
{
    Item*             it = Item_create(NULL, NULL, NULL, NULL, NULL);
    Composition*      co = Composition_create(NULL, NULL, NULL, NULL, NULL);
    ComposableVector* composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) it);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool resultOK = Composition_set_children(co, composableVector, errorStatus);
    Composition* parent = Composable_parent((Composable*) it);
    EXPECT_EQ(parent, co);

    Composition* co2 = Composition_create(NULL, NULL, NULL, NULL, NULL);

    Composition_remove_child(co, 0, errorStatus);

    resultOK = Composition_set_children(co2, composableVector, errorStatus);

    parent = Composable_parent((Composable*) it);
    EXPECT_EQ(parent, co2);

    SerializableObject_possibly_delete((SerializableObject*) co);
    co = NULL;
    //    SerializableObject_possibly_delete((SerializableObject*) co2);
    //    co2 = NULL; //TODO Fix segfault
    ComposableVector_destroy(composableVector);
    composableVector = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOCompositionTests, RemoveActuallyRemovesTest)
{
    Track*           track       = Track_create(NULL, NULL, NULL, NULL);
    Clip*            clip        = Clip_create(NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Composition_append_child(
        (Composition*) track, (Composable*) clip, errorStatus);

    ComposableRetainerVector* children =
        Composition_children((Composition*) track);
    RetainerComposable* child     = ComposableRetainerVector_at(children, 0);
    Composable*         child_val = RetainerComposable_take_value(child);

    EXPECT_EQ((Composable*) clip, child_val);

    Composition_remove_child((Composition*) track, 0, errorStatus);

    ComposableRetainerVector_destroy(children);
    children = NULL;
    RetainerComposable_managed_destroy(child);

    children = Composition_children((Composition*) track);
    EXPECT_EQ(ComposableRetainerVector_size(children), 0);
    ComposableRetainerVector_destroy(children);
}

TEST_F(OTIOStackTests, ConstructorTest)
{
    Stack* st = Stack_create("test", NULL, NULL, NULL, NULL);
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) st),
        "test");
    SerializableObject_possibly_delete((SerializableObject*) st);
    st = NULL;
}

TEST_F(OTIOStackTests, SerializeTest)
{
    Stack*           st          = Stack_create("test", NULL, NULL, NULL, NULL);
    Clip*            clip        = Clip_create("testClip", NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool             insertOK    = Composition_insert_child(
        (Composition*) st, 0, (Composable*) clip, errorStatus);

    ASSERT_TRUE(insertOK);
    Any* stack_any =
        create_safely_typed_any_serializable_object((SerializableObject*) st);
    const char* encoded = serialize_json_to_string(stack_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) st);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) st, decoded_object));

    SerializableObject_possibly_delete((SerializableObject*) st);
    st = NULL;
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOStackTests, TrimChildRangeTest)
{
    Track* tr = Track_create("foo", NULL, NULL, NULL);
    Stack* st = Stack_create("foo", NULL, NULL, NULL, NULL);

    Composition* comp[] = { (Composition*) tr, (Composition*) st };

    for(int i = 0; i < sizeof(comp) / sizeof(comp[0]); i++)
    {
        Composition* co = comp[i];

        RationalTime* start_time = RationalTime_create(100, 24);
        RationalTime* duration   = RationalTime_create(50, 24);
        TimeRange*    tr =
            TimeRange_create_with_start_time_and_duration(start_time, duration);
        Item_set_source_range((Item*) co, tr);
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        start_time = RationalTime_create(110, 24);
        duration   = RationalTime_create(30, 24);
        TimeRange* r =
            TimeRange_create_with_start_time_and_duration(start_time, duration);
        TimeRange* st_trim_child_range = Composition_trim_child_range(co, r);
        EXPECT_TRUE(TimeRange_equal(st_trim_child_range, r));
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        TimeRange_destroy(tr);
        TimeRange_destroy(r);
        TimeRange_destroy(st_trim_child_range);

        start_time = RationalTime_create(0, 24);
        duration   = RationalTime_create(30, 24);
        r = TimeRange_create_with_start_time_and_duration(start_time, duration);
        st_trim_child_range = Composition_trim_child_range(co, r);
        EXPECT_EQ(st_trim_child_range, nullptr);
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        TimeRange_destroy(r);
        TimeRange_destroy(st_trim_child_range);

        start_time = RationalTime_create(1000, 24);
        duration   = RationalTime_create(30, 24);
        r = TimeRange_create_with_start_time_and_duration(start_time, duration);
        st_trim_child_range = Composition_trim_child_range(co, r);
        EXPECT_EQ(st_trim_child_range, nullptr);
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        TimeRange_destroy(r);
        TimeRange_destroy(st_trim_child_range);

        start_time = RationalTime_create(90, 24);
        duration   = RationalTime_create(30, 24);
        r = TimeRange_create_with_start_time_and_duration(start_time, duration);
        st_trim_child_range = Composition_trim_child_range(co, r);
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        start_time = RationalTime_create(100, 24);
        duration   = RationalTime_create(20, 24);
        tr =
            TimeRange_create_with_start_time_and_duration(start_time, duration);
        EXPECT_TRUE(TimeRange_equal(tr, st_trim_child_range));
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        TimeRange_destroy(tr);
        TimeRange_destroy(r);
        TimeRange_destroy(st_trim_child_range);

        start_time = RationalTime_create(110, 24);
        duration   = RationalTime_create(50, 24);
        r = TimeRange_create_with_start_time_and_duration(start_time, duration);
        st_trim_child_range = Composition_trim_child_range(co, r);
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        start_time = RationalTime_create(110, 24);
        duration   = RationalTime_create(40, 24);
        tr =
            TimeRange_create_with_start_time_and_duration(start_time, duration);
        EXPECT_TRUE(TimeRange_equal(tr, st_trim_child_range));
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        TimeRange_destroy(tr);
        TimeRange_destroy(r);
        TimeRange_destroy(st_trim_child_range);

        start_time = RationalTime_create(90, 24);
        duration   = RationalTime_create(1000, 24);
        r = TimeRange_create_with_start_time_and_duration(start_time, duration);
        st_trim_child_range = Composition_trim_child_range(co, r);
        RationalTime_destroy(start_time);
        RationalTime_destroy(duration);
        TimeRange* co_source_range = Item_source_range((Item*) co);
        EXPECT_TRUE(TimeRange_equal(co_source_range, st_trim_child_range));
        TimeRange_destroy(r);
        TimeRange_destroy(st_trim_child_range);
        TimeRange_destroy(co_source_range);
    }
    SerializableObject_possibly_delete((SerializableObject*) tr);
    tr = NULL;
    SerializableObject_possibly_delete((SerializableObject*) st);
    st = NULL;
}

TEST_F(OTIOStackTests, RangeOfChildTest)
{
    RationalTime* start_time = RationalTime_create(100, 24);
    RationalTime* duration   = RationalTime_create(50, 24);
    TimeRange*    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip1 = Clip_create("clip1", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);
    start_time = RationalTime_create(101, 24);
    duration   = RationalTime_create(50, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip2 = Clip_create("clip2", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);
    start_time = RationalTime_create(102, 24);
    duration   = RationalTime_create(50, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip3 = Clip_create("clip3", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);

    Stack*           st          = Stack_create("foo", NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Composition_insert_child(
        (Composition*) st, 0, (Composable*) clip1, errorStatus);
    Composition_insert_child(
        (Composition*) st, 1, (Composable*) clip2, errorStatus);
    Composition_insert_child(
        (Composition*) st, 2, (Composable*) clip3, errorStatus);

    /* stack should be as long as longest child */
    RationalTime* length = RationalTime_create(50, 24);
    RationalTime* st_duration =
        Composable_duration((Composable*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(length, st_duration));
    RationalTime_destroy(length);
    RationalTime_destroy(st_duration);

    RationalTime* zero_time = RationalTime_create(0, 24);
    /* stacked items should all start at time zero */
    TimeRange* range_at_0 = Stack_range_of_child_at_index(st, 0, errorStatus);
    TimeRange* range_at_1 = Stack_range_of_child_at_index(st, 1, errorStatus);
    TimeRange* range_at_2 = Stack_range_of_child_at_index(st, 2, errorStatus);
    RationalTime* start0  = TimeRange_start_time(range_at_0);
    RationalTime* start1  = TimeRange_start_time(range_at_1);
    RationalTime* start2  = TimeRange_start_time(range_at_2);
    EXPECT_TRUE(RationalTime_equal(start0, zero_time));
    EXPECT_TRUE(RationalTime_equal(start1, zero_time));
    EXPECT_TRUE(RationalTime_equal(start2, zero_time));
    RationalTime_destroy(start0);
    start0 = NULL;
    RationalTime_destroy(start1);
    start1 = NULL;
    RationalTime_destroy(start2);
    start2 = NULL;
    RationalTime_destroy(zero_time);
    zero_time = NULL;

    RationalTime* duration0     = TimeRange_duration(range_at_0);
    RationalTime* duration1     = TimeRange_duration(range_at_1);
    RationalTime* duration2     = TimeRange_duration(range_at_2);
    RationalTime* duration_time = RationalTime_create(50, 24);
    EXPECT_TRUE(RationalTime_equal(duration0, duration_time));
    EXPECT_TRUE(RationalTime_equal(duration1, duration_time));
    EXPECT_TRUE(RationalTime_equal(duration2, duration_time));

    RationalTime_destroy(duration0);
    duration0 = NULL;
    RationalTime_destroy(duration1);
    duration1 = NULL;
    RationalTime_destroy(duration2);
    duration2 = NULL;
    RationalTime_destroy(duration_time);
    duration_time = NULL;
    TimeRange_destroy(range_at_0);
    range_at_0 = NULL;
    TimeRange_destroy(range_at_1);
    range_at_1 = NULL;
    TimeRange_destroy(range_at_2);
    range_at_2 = NULL;
    SerializableObject_possibly_delete((SerializableObject*) st);
    st = NULL;
}

TEST_F(OTIOStackTests, RangeOfChildWithDurationTest)
{
    RationalTime* start_time = RationalTime_create(100, 24);
    RationalTime* duration   = RationalTime_create(50, 24);
    TimeRange*    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip1 = Clip_create("clip1", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);
    start_time = RationalTime_create(101, 24);
    duration   = RationalTime_create(50, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip2 = Clip_create("clip2", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);
    start_time = RationalTime_create(102, 24);
    duration   = RationalTime_create(50, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip3 = Clip_create("clip3", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);

    start_time = RationalTime_create(5, 24);
    duration   = RationalTime_create(5, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);

    Stack*           st          = Stack_create("foo", NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Composition_insert_child(
        (Composition*) st, 0, (Composable*) clip1, errorStatus);
    Composition_insert_child(
        (Composition*) st, 1, (Composable*) clip2, errorStatus);
    Composition_insert_child(
        (Composition*) st, 2, (Composable*) clip3, errorStatus);

    Item_set_source_range((Item*) st, st_sourcerange);
    TimeRange_destroy(st_sourcerange);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);

    /* range always returns the pre-trimmed range.  To get the post-trim
     * range, call .trimmed_range()
     */
    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) st);
    ComposableRetainerVectorIterator* it =
        ComposableRetainerVector_begin(composableRetainerVector);
    RetainerComposable* retainerComposable =
        ComposableRetainerVectorIterator_value(it);
    Composable* st_0 = RetainerComposable_take_value(retainerComposable);
    TimeRange*  child_range =
        Composition_range_of_child((Composition*) st, st_0, errorStatus);
    start_time = RationalTime_create(0, 24);
    duration   = RationalTime_create(50, 24);
    TimeRange* time_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    EXPECT_TRUE(TimeRange_equal(time_range, child_range));
    TimeRange_destroy(time_range);
    TimeRange_destroy(child_range);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);

    RationalTime* rt  = RationalTime_create(25, 24);
    RationalTime* rt2 = RationalTime_create(125, 24);
    RationalTime* st_transformed_time =
        Item_transformed_time((Item*) st, rt, (Item*) st_0, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, rt2));
    RationalTime_destroy(st_transformed_time);

    st_transformed_time =
        Item_transformed_time((Item*) st_0, rt2, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, rt));
    RationalTime_destroy(st_transformed_time);
    RationalTime_destroy(rt);
    RationalTime_destroy(rt2);

    /* trimmed_ functions take into account the source_range */
    TimeRange* st_trimmed_range_child_0 =
        Stack_trimmed_range_of_child_at_index(st, 0, errorStatus);
    st_sourcerange = Item_source_range((Item*) st);
    EXPECT_TRUE(TimeRange_equal(st_trimmed_range_child_0, st_sourcerange));
    TimeRange_destroy(st_trimmed_range_child_0);
    TimeRange_destroy(st_sourcerange);

    st_trimmed_range_child_0 = Composition_trimmed_range_of_child(
        (Composition*) st, (Composable*) st_0, errorStatus);
    start_time = RationalTime_create(5, 24);
    duration   = RationalTime_create(5, 24);
    time_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    EXPECT_TRUE(TimeRange_equal(st_trimmed_range_child_0, time_range));
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(time_range);

    /* get the trimmed range in the parent */
    TimeRange* st_0_trimmed_range_in_parent =
        Item_trimmed_range_in_parent((Item*) st_0, errorStatus);
    EXPECT_TRUE(TimeRange_equal(
        st_0_trimmed_range_in_parent, st_trimmed_range_child_0));
    TimeRange_destroy(st_0_trimmed_range_in_parent);

    TimeRange_destroy(st_trimmed_range_child_0);
    ComposableRetainerVector_destroy(composableRetainerVector);
    ComposableRetainerVectorIterator_destroy(it);
    RetainerComposable_managed_destroy(retainerComposable);

    Clip*      errorClip = Clip_create(NULL, NULL, NULL, NULL);
    TimeRange* errorTime =
        Item_trimmed_range_in_parent((Item*) errorClip, errorStatus);
    OTIO_ErrorStatus_Outcome outcome = OTIOErrorStatus_get_outcome(errorStatus);
    EXPECT_EQ(outcome, 18);
    TimeRange_destroy(errorTime);
    errorTime = NULL;
    SerializableObject_possibly_delete((SerializableObject*) errorClip);
    errorClip = NULL;

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    SerializableObject_possibly_delete((SerializableObject*) st);
    st = NULL;
}

TEST_F(OTIOStackTests, TransformedTimeTest)
{
    RationalTime* start_time = RationalTime_create(100, 24);
    RationalTime* duration   = RationalTime_create(50, 24);
    TimeRange*    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip1 = Clip_create("clip1", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);
    start_time = RationalTime_create(101, 24);
    duration   = RationalTime_create(50, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip2 = Clip_create("clip2", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);
    start_time = RationalTime_create(102, 24);
    duration   = RationalTime_create(50, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip3 = Clip_create("clip3", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);

    start_time = RationalTime_create(5, 24);
    duration   = RationalTime_create(5, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);

    Stack*           st          = Stack_create("foo", NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Composition_insert_child(
        (Composition*) st, 0, (Composable*) clip1, errorStatus);
    Composition_insert_child(
        (Composition*) st, 1, (Composable*) clip2, errorStatus);
    Composition_insert_child(
        (Composition*) st, 2, (Composable*) clip3, errorStatus);

    Item_set_source_range((Item*) st, st_sourcerange);
    TimeRange_destroy(st_sourcerange);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) st);
    RetainerComposable* rc0 =
        ComposableRetainerVector_at(composableRetainerVector, 0);
    RetainerComposable* rc1 =
        ComposableRetainerVector_at(composableRetainerVector, 1);
    RetainerComposable* rc2 =
        ComposableRetainerVector_at(composableRetainerVector, 2);
    Composable* c0 = RetainerComposable_take_value(rc0);
    Composable* c1 = RetainerComposable_take_value(rc1);
    Composable* c2 = RetainerComposable_take_value(rc2);
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) c0),
        "clip1");
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) c1),
        "clip2");
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) c2),
        "clip3");

    ComposableRetainerVector_destroy(composableRetainerVector);

    RationalTime* test_time           = RationalTime_create(0, 24);
    RationalTime* test_time2          = RationalTime_create(100, 24);
    RationalTime* st_transformed_time = Item_transformed_time(
        (Item*) st, test_time, (Item*) clip1, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    /* ensure that transformed_time does not edit in place */
    RationalTime* verify_test_time = RationalTime_create(0, 24);
    EXPECT_TRUE(RationalTime_equal(test_time, verify_test_time));
    RationalTime_destroy(verify_test_time);
    RationalTime_destroy(test_time);

    test_time           = RationalTime_create(0, 24);
    test_time2          = RationalTime_create(101, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) st, test_time, (Item*) clip2, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(0, 24);
    test_time2          = RationalTime_create(102, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) st, test_time, (Item*) clip3, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(50, 24);
    test_time2          = RationalTime_create(150, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) st, test_time, (Item*) clip1, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(50, 24);
    test_time2          = RationalTime_create(151, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) st, test_time, (Item*) clip2, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(50, 24);
    test_time2          = RationalTime_create(152, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) st, test_time, (Item*) clip3, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(100, 24);
    test_time2          = RationalTime_create(0, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) clip1, test_time, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(101, 24);
    test_time2          = RationalTime_create(0, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) clip2, test_time, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(102, 24);
    test_time2          = RationalTime_create(0, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) clip3, test_time, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(150, 24);
    test_time2          = RationalTime_create(50, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) clip1, test_time, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(151, 24);
    test_time2          = RationalTime_create(50, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) clip2, test_time, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    test_time           = RationalTime_create(152, 24);
    test_time2          = RationalTime_create(50, 24);
    st_transformed_time = Item_transformed_time(
        (Item*) clip3, test_time, (Item*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(st_transformed_time, test_time2));
    RationalTime_destroy(test_time);
    RationalTime_destroy(test_time2);
    RationalTime_destroy(st_transformed_time);

    SerializableObject_possibly_delete((SerializableObject*) st);
    st = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOTrackTests, SerializeTest)
{
    Track*           sq          = Track_create("foo", NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Any*             sq_any =
        create_safely_typed_any_serializable_object((SerializableObject*) sq);
    const char* encoded = serialize_json_to_string(sq_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) sq);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) sq, decoded_object));

    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOTrackTests, InstancingTest)
{
    RationalTime* length    = RationalTime_create(5, 1);
    RationalTime* zero_time = RationalTime_create(0, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(zero_time, length);
    Item*            it          = Item_create(NULL, tr, NULL, NULL, NULL);
    Track*           sq          = Track_create(NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool             insertOK    = Composition_insert_child(
        (Composition*) sq, 0, (Composable*) it, errorStatus);
    ASSERT_TRUE(insertOK);
    TimeRange* sq_range_of_child_0 =
        Track_range_of_child_at_index(sq, 0, errorStatus);
    EXPECT_TRUE(TimeRange_equal(sq_range_of_child_0, tr));

    /* Can't put item on a composition if it's already in one */
    Track* test_track = Track_create(NULL, NULL, NULL, NULL);
    insertOK          = Composition_insert_child(
        (Composition*) test_track, 0, (Composable*) it, errorStatus);
    ASSERT_FALSE(insertOK);
    SerializableObject_possibly_delete((SerializableObject*) test_track);
    test_track = NULL;

    /* Instancing is not allowed */
    ComposableVector* composableVector = ComposableVector_create();
    ComposableVector_push_back(composableVector, (Composable*) it);
    ComposableVector_push_back(composableVector, (Composable*) it);
    ComposableVector_push_back(composableVector, (Composable*) it);
    test_track = Track_create(NULL, NULL, NULL, NULL);
    insertOK   = Composition_set_children(
        (Composition*) test_track, composableVector, errorStatus);
    ASSERT_FALSE(insertOK);
    SerializableObject_possibly_delete((SerializableObject*) test_track);
    test_track = NULL;
    ComposableVector_destroy(composableVector);
    composableVector = NULL;

    /*inserting duplicates should raise error and have no side effects*/
    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) sq);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 1);
    ComposableRetainerVector_destroy(composableRetainerVector);
    insertOK = Composition_append_child(
        (Composition*) sq, (Composable*) it, errorStatus);
    ASSERT_FALSE(insertOK);
    composableRetainerVector = Composition_children((Composition*) sq);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 1);
    ComposableRetainerVector_destroy(composableRetainerVector);

    insertOK = Composition_insert_child(
        (Composition*) sq, 1, (Composable*) it, errorStatus);
    ASSERT_FALSE(insertOK);
    composableRetainerVector = Composition_children((Composition*) sq);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 1);
    ComposableRetainerVector_destroy(composableRetainerVector);

    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
    RationalTime_destroy(length);
    length = NULL;
    RationalTime_destroy(zero_time);
    zero_time = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
}

TEST_F(OTIOTrackTests, DeleteParentContainerTest)
{
    /* deleting the parent container should null out the parent pointer */
    Item*            it          = Item_create(NULL, NULL, NULL, NULL, NULL);
    Track*           sq          = Track_create(NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool             insertOK    = Composition_insert_child(
        (Composition*) sq, 0, (Composable*) it, errorStatus);
    ASSERT_TRUE(insertOK);
    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq                  = NULL;
    Composition* parent = Composable_parent((Composable*) it);
    EXPECT_EQ(parent, nullptr);
}

TEST_F(OTIOTrackTests, TransactionalTest)
{
    //    Item*            item        = Item_create(NULL, NULL, NULL, NULL, NULL);
    //    Track*           trackA      = Track_create(NULL, NULL, NULL, NULL);
    //    Track*           trackB      = Track_create(NULL, NULL, NULL, NULL);
    //    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    //    Item*            item1       = Item_create(NULL, NULL, NULL, NULL, NULL);
    //    Item*            item2       = Item_create(NULL, NULL, NULL, NULL, NULL);
    //    Item*            item3       = Item_create(NULL, NULL, NULL, NULL, NULL);
    //
    //    SerializableObject* itemClone1 =
    //        SerializableObject_clone((SerializableObject*) item, errorStatus);
    //
    //    SerializableObject* itemClone2 =
    //        SerializableObject_clone((SerializableObject*) item, errorStatus);
    // TODO segfault here

    //    SerializableObject* itemClone3 =
    //        SerializableObject_clone((SerializableObject*) item, errorStatus);
    //        SerializableObject* itemClone3 =
    //            SerializableObject_clone((SerializableObject*) itemClone2, errorStatus);
    //    SerializableObject* itemClone4 =
    //        SerializableObject_clone((SerializableObject*) itemClone1, errorStatus);
    //    SerializableObject* itemClone5 =
    //        SerializableObject_clone((SerializableObject*) item, errorStatus);
    //    SerializableObject* itemClone6 =
    //        SerializableObject_clone((SerializableObject*) itemClone1, errorStatus);
    //    bool insertOK = false;
    //
    //    insertOK = Composition_insert_child(
    //        (Composition*) trackA, 0, (Composable*) item1, errorStatus);
    //    ASSERT_TRUE(insertOK);
    //    insertOK = Composition_insert_child(
    //        (Composition*) trackA, 1, (Composable*) item2, errorStatus);
    //    ASSERT_TRUE(insertOK);
    //    insertOK = Composition_insert_child(
    //        (Composition*) trackA, 2, (Composable*) item3, errorStatus);
    //    ASSERT_TRUE(insertOK);
    //    ComposableRetainerVector* composableRetainerVector =
    //        Composition_children((Composition*) trackA);
    //    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 3);
    //    ComposableRetainerVector_destroy(composableRetainerVector);
    //    composableRetainerVector = NULL;

    //    insertOK = Composition_insert_child(
    //        (Composition*) trackB, 0, (Composable*) itemClone4, errorStatus);
    //    ASSERT_TRUE(insertOK);
    //    insertOK = Composition_insert_child(
    //        (Composition*) trackB, 1, (Composable*) itemClone5, errorStatus);
    //    ASSERT_TRUE(insertOK);
    //    insertOK = Composition_insert_child(
    //        (Composition*) trackB, 2, (Composable*) itemClone6, errorStatus);
    //    ASSERT_TRUE(insertOK);
    //    composableRetainerVector = Composition_children((Composition*) trackA);
    //    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 3);
    //    ComposableRetainerVector_destroy(composableRetainerVector);
    //    composableRetainerVector = NULL;
}

TEST_F(OTIOTrackTests, RangeTest)
{
    RationalTime* length    = RationalTime_create(5, 1);
    RationalTime* zero_time = RationalTime_create(0, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(zero_time, length);
    Item*            it          = Item_create(NULL, tr, NULL, NULL, NULL);
    Track*           sq          = Track_create(NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool             insertOK    = Composition_append_child(
        (Composition*) sq, (Composable*) it, errorStatus);
    ASSERT_TRUE(insertOK);
    TimeRange* sq_range_child_0 =
        Track_range_of_child_at_index(sq, 0, errorStatus);
    EXPECT_TRUE(TimeRange_equal(sq_range_child_0, tr));

    Item* it2 = Item_create(NULL, tr, NULL, NULL, NULL);
    Item* it3 = Item_create(NULL, tr, NULL, NULL, NULL);
    Item* it4 = Item_create(NULL, tr, NULL, NULL, NULL);
    insertOK  = Composition_append_child(
        (Composition*) sq, (Composable*) it2, errorStatus);
    ASSERT_TRUE(insertOK);
    insertOK = Composition_append_child(
        (Composition*) sq, (Composable*) it3, errorStatus);
    ASSERT_TRUE(insertOK);
    insertOK = Composition_append_child(
        (Composition*) sq, (Composable*) it4, errorStatus);
    ASSERT_TRUE(insertOK);

    TimeRange_destroy(sq_range_child_0);
    TimeRange_destroy(tr);
    RationalTime_destroy(length);
    RationalTime_destroy(zero_time);

    TimeRange* sq_range_child_1 =
        Track_range_of_child_at_index(sq, 1, errorStatus);
    RationalTime* start_time = RationalTime_create(5, 1);
    RationalTime* duration   = RationalTime_create(5, 1);
    tr = TimeRange_create_with_start_time_and_duration(start_time, duration);
    EXPECT_TRUE(TimeRange_equal(tr, sq_range_child_1));
    TimeRange_destroy(sq_range_child_1);
    TimeRange_destroy(tr);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);

    sq_range_child_0 = Track_range_of_child_at_index(sq, 0, errorStatus);
    start_time       = RationalTime_create(0, 1);
    duration         = RationalTime_create(5, 1);
    tr = TimeRange_create_with_start_time_and_duration(start_time, duration);
    EXPECT_TRUE(TimeRange_equal(tr, sq_range_child_0));
    TimeRange_destroy(sq_range_child_0);
    TimeRange_destroy(tr);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);

    TimeRange* sq_range_child_minus_1 =
        Track_range_of_child_at_index(sq, -1, errorStatus);
    start_time = RationalTime_create(15, 1);
    duration   = RationalTime_create(5, 1);
    tr = TimeRange_create_with_start_time_and_duration(start_time, duration);
    EXPECT_TRUE(TimeRange_equal(tr, sq_range_child_minus_1));
    TimeRange_destroy(sq_range_child_minus_1);
    TimeRange_destroy(tr);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);

    TimeRange* sq_range_child_minus_error =
        Track_range_of_child_at_index(sq, 11, errorStatus);
    OTIO_ErrorStatus_Outcome outcome = OTIOErrorStatus_get_outcome(errorStatus);
    EXPECT_EQ(outcome, 13);
    TimeRange_destroy(sq_range_child_minus_error);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();

    RationalTime* sq_duration      = Item_duration((Item*) sq, errorStatus);
    RationalTime* duration_compare = RationalTime_create(20, 1);
    EXPECT_TRUE(RationalTime_equal(sq_duration, duration_compare));
    RationalTime_destroy(sq_duration);
    RationalTime_destroy(duration_compare);

    /* add a transition to either side */
    TimeRange* range_of_child_3 =
        Track_range_of_child_at_index(sq, 3, errorStatus);
    RationalTime* in_offset  = RationalTime_create(10, 24);
    RationalTime* out_offset = RationalTime_create(12, 24);
    TimeRange*    range_of_item =
        Track_range_of_child_at_index(sq, 3, errorStatus);
    Transition* trx1 =
        Transition_create(NULL, NULL, in_offset, out_offset, NULL);
    Transition* trx2 =
        Transition_create(NULL, NULL, in_offset, out_offset, NULL);
    Transition* trx3 =
        Transition_create(NULL, NULL, in_offset, out_offset, NULL);
    insertOK = Composition_insert_child(
        (Composition*) sq, 0, (Composable*) trx1, errorStatus);
    ASSERT_TRUE(insertOK);
    insertOK = Composition_insert_child(
        (Composition*) sq, 3, (Composable*) trx2, errorStatus);
    ASSERT_TRUE(insertOK);
    insertOK = Composition_append_child(
        (Composition*) sq, (Composable*) trx3, errorStatus);
    ASSERT_TRUE(insertOK);
    TimeRange_destroy(range_of_item);

    /* range of Transition */
    start_time = RationalTime_create(230, 24);
    duration   = RationalTime_create(22, 24);
    tr = TimeRange_create_with_start_time_and_duration(start_time, duration);
    range_of_item = Track_range_of_child_at_index(sq, 3, errorStatus);
    EXPECT_TRUE(TimeRange_equal(tr, range_of_item));
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(tr);
    TimeRange_destroy(range_of_item);

    start_time = RationalTime_create(470, 24);
    duration   = RationalTime_create(22, 24);
    tr = TimeRange_create_with_start_time_and_duration(start_time, duration);
    range_of_item = Track_range_of_child_at_index(sq, -1, errorStatus);
    EXPECT_TRUE(TimeRange_equal(tr, range_of_item));
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(tr);
    TimeRange_destroy(range_of_item);

    tr = Track_range_of_child_at_index(sq, 5, errorStatus);
    EXPECT_TRUE(TimeRange_equal(tr, range_of_child_3));
    TimeRange_destroy(tr);
    TimeRange_destroy(range_of_child_3);

    sq_duration = Item_duration((Item*) sq, errorStatus);
    /* duration_compare = length x 4 + in_offset + out_offset */
    duration_compare = RationalTime_create(20 + 22.0 / 24.0, 1);
    EXPECT_TRUE(RationalTime_equal(sq_duration, duration_compare));
    RationalTime_destroy(sq_duration);
    RationalTime_destroy(duration_compare);

    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
}

TEST_F(OTIOTrackTests, RangeOfChildTest)
{
    Track*        sq         = Track_create("foo", NULL, NULL, NULL);
    RationalTime* start_time = RationalTime_create(100, 24);
    RationalTime* duration   = RationalTime_create(50, 24);
    TimeRange*    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip1 = Clip_create("clip1", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);
    start_time = RationalTime_create(101, 24);
    duration   = RationalTime_create(50, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip2 = Clip_create("clip2", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);
    start_time = RationalTime_create(102, 24);
    duration   = RationalTime_create(50, 24);
    st_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip3 = Clip_create("clip3", NULL, st_sourcerange, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(st_sourcerange);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    bool appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) clip1, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) clip2, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) clip3, errorStatus);
    ASSERT_TRUE(appendOK);

    /* The Track should be as long as the children summed up */
    RationalTime* sq_duration      = Item_duration((Item*) sq, errorStatus);
    RationalTime* duration_compare = RationalTime_create(150, 24);
    EXPECT_TRUE(RationalTime_equal(sq_duration, duration_compare));
    RationalTime_destroy(sq_duration);
    RationalTime_destroy(duration_compare);

    /* Sequenced items should all land end-to-end */
    duration_compare = RationalTime_create(50, 24);
    TimeRange* range_of_child_index =
        Track_range_of_child_at_index(sq, 0, errorStatus);
    RationalTime* range_time     = TimeRange_start_time(range_of_child_index);
    RationalTime* range_duration = TimeRange_duration(range_of_child_index);
    RationalTime* time_compare   = RationalTime_create(0, 1);
    EXPECT_TRUE(RationalTime_equal(range_time, time_compare));
    EXPECT_TRUE(RationalTime_equal(duration_compare, range_duration));
    TimeRange_destroy(range_of_child_index);
    RationalTime_destroy(range_time);
    RationalTime_destroy(range_duration);
    RationalTime_destroy(time_compare);

    range_of_child_index = Track_range_of_child_at_index(sq, 1, errorStatus);
    range_time           = TimeRange_start_time(range_of_child_index);
    range_duration       = TimeRange_duration(range_of_child_index);
    time_compare         = RationalTime_create(50, 24);
    EXPECT_TRUE(RationalTime_equal(range_time, time_compare));
    EXPECT_TRUE(RationalTime_equal(duration_compare, range_duration));
    TimeRange_destroy(range_of_child_index);
    RationalTime_destroy(range_time);
    RationalTime_destroy(range_duration);
    RationalTime_destroy(time_compare);

    range_of_child_index = Track_range_of_child_at_index(sq, 2, errorStatus);
    range_time           = TimeRange_start_time(range_of_child_index);
    range_duration       = TimeRange_duration(range_of_child_index);
    time_compare         = RationalTime_create(100, 24);
    EXPECT_TRUE(RationalTime_equal(range_time, time_compare));
    EXPECT_TRUE(RationalTime_equal(duration_compare, range_duration));
    RationalTime_destroy(range_time);
    RationalTime_destroy(range_duration);
    RationalTime_destroy(time_compare);
    RationalTime_destroy(duration_compare);

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) sq);
    RetainerComposable* retainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 2);
    Composable* retainerComposableValue =
        RetainerComposable_take_value(retainerComposable);
    TimeRange* range_compare = Composition_range_of_child(
        (Composition*) sq, retainerComposableValue, errorStatus);
    EXPECT_TRUE(TimeRange_equal(range_compare, range_of_child_index));
    TimeRange_destroy(range_of_child_index);
    TimeRange_destroy(range_compare);

    /* should trim 5 frames off the front, and 5 frames off the back */
    start_time = RationalTime_create(5, 24);
    duration   = RationalTime_create(140, 24);
    TimeRange* sq_sourcerange =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Item_set_source_range((Item*) sq, sq_sourcerange);
    TimeRange* sq_trimmed_range_of_child_index =
        Track_trimmed_range_of_child_at_index(sq, 0, errorStatus);
    RationalTime_destroy(duration);
    duration = RationalTime_create(45, 24);
    range_compare =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    RationalTime_destroy(duration);
    RationalTime_destroy(start_time);
    EXPECT_TRUE(
        TimeRange_equal(range_compare, sq_trimmed_range_of_child_index));
    TimeRange_destroy(range_compare);
    TimeRange_destroy(sq_trimmed_range_of_child_index);
    TimeRange_destroy(sq_sourcerange);

    sq_trimmed_range_of_child_index =
        Track_trimmed_range_of_child_at_index(sq, 1, errorStatus);
    range_compare = Track_range_of_child_at_index(sq, 1, errorStatus);
    EXPECT_TRUE(
        TimeRange_equal(range_compare, sq_trimmed_range_of_child_index));
    TimeRange_destroy(range_compare);
    TimeRange_destroy(sq_trimmed_range_of_child_index);

    sq_trimmed_range_of_child_index =
        Track_trimmed_range_of_child_at_index(sq, 2, errorStatus);
    start_time = RationalTime_create(100, 24);
    duration   = RationalTime_create(45, 24);
    range_compare =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    EXPECT_TRUE(
        TimeRange_equal(range_compare, sq_trimmed_range_of_child_index));
    TimeRange_destroy(range_compare);
    TimeRange_destroy(sq_trimmed_range_of_child_index);
    RationalTime_destroy(duration);
    RationalTime_destroy(start_time);

    /* get the trimmed range in the parent */
    retainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 0);
    retainerComposableValue = RetainerComposable_take_value(retainerComposable);
    TimeRange* trimmed_range_in_parent = Item_trimmed_range_in_parent(
        (Item*) retainerComposableValue, errorStatus);
    TimeRange* trimmed_range_of_child = Composition_trimmed_range_of_child(
        (Composition*) sq, retainerComposableValue, errorStatus);
    EXPECT_TRUE(
        TimeRange_equal(trimmed_range_in_parent, trimmed_range_of_child));
    TimeRange_destroy(trimmed_range_of_child);
    TimeRange_destroy(trimmed_range_in_parent);

    ComposableRetainerVector_destroy(composableRetainerVector);
    composableRetainerVector = NULL;
    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
    RetainerComposable_managed_destroy(retainerComposable);
    retainerComposable = NULL;
}