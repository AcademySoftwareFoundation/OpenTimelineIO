#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <copentime/timeRange.h>
#include <copentimelineio/clip.h>
#include <copentimelineio/composable.h>
#include <copentimelineio/composableVector.h>
#include <copentimelineio/composition.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/gap.h>
#include <copentimelineio/item.h>
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/stack.h>
#include <copentimelineio/timeline.h>
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
    void        SetUp() override { sample_data_dir = xstr(SAMPLE_DATA_DIR); }
    void        TearDown() override {}
    const char* sample_data_dir;
};

class OTIOEdgeCases : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

class OTIONestingTest : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}

    struct ClipWrapperPair
    {
        Clip*  clip;
        Stack* wrapper;
    };
    typedef struct ClipWrapperPair ClipWrapperPair;

    ClipWrapperPair _nest(Clip* item, int index)
    {
        ClipWrapperPair clipWrapperPair;
        clipWrapperPair.clip    = NULL;
        clipWrapperPair.wrapper = NULL;

        if(item == NULL) return clipWrapperPair;

        Composition* parent = Composable_parent((Composable*) item);

        if(parent == NULL) { return clipWrapperPair; }
        OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
        Stack*           wrapper = Stack_create(NULL, NULL, NULL, NULL, NULL);

        Clip* clip = (Clip*) SerializableObject_clone(
            (SerializableObject*) item, errorStatus);

        /* now put the item inside the wrapper */
        bool appendOK = Composition_append_child(
            (Composition*) wrapper, (Composable*) clip, errorStatus);

        /* swap out the item for the wrapper */
        bool setOK = Composition_set_child(
            (Composition*) parent, index, (Composable*) wrapper, errorStatus);

        clipWrapperPair.clip    = clip;
        clipWrapperPair.wrapper = wrapper;
        return clipWrapperPair;
    }
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
    Any*        decoded = /** allocate memory for destinantion */
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

    /** stack should be as long as longest child */
    RationalTime* length = RationalTime_create(50, 24);
    RationalTime* st_duration =
        Composable_duration((Composable*) st, errorStatus);
    EXPECT_TRUE(RationalTime_equal(length, st_duration));
    RationalTime_destroy(length);
    RationalTime_destroy(st_duration);

    RationalTime* zero_time = RationalTime_create(0, 24);
    /** stacked items should all start at time zero */
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

    /** range always returns the pre-trimmed range.  To get the post-trim
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

    /** trimmed_ functions take into account the source_range */
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

    /** get the trimmed range in the parent */
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

    /** ensure that transformed_time does not edit in place */
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
    Any*        decoded = /** allocate memory for destinantion */
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

    /** Can't put item on a composition if it's already in one */
    Track* test_track = Track_create(NULL, NULL, NULL, NULL);
    insertOK          = Composition_insert_child(
        (Composition*) test_track, 0, (Composable*) it, errorStatus);
    ASSERT_FALSE(insertOK);
    SerializableObject_possibly_delete((SerializableObject*) test_track);
    test_track = NULL;

    /** Instancing is not allowed */
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

    /**inserting duplicates should raise error and have no side effects*/
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
    /** deleting the parent container should null out the parent pointer */
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

    /** add a transition to either side */
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

    /** range of Transition */
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
    /** duration_compare = length x 4 + in_offset + out_offset */
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

    /** The Track should be as long as the children summed up */
    RationalTime* sq_duration      = Item_duration((Item*) sq, errorStatus);
    RationalTime* duration_compare = RationalTime_create(150, 24);
    EXPECT_TRUE(RationalTime_equal(sq_duration, duration_compare));
    RationalTime_destroy(sq_duration);
    RationalTime_destroy(duration_compare);

    /** Sequenced items should all land end-to-end */
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

    /** should trim 5 frames off the front, and 5 frames off the back */
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

    /** get the trimmed range in the parent */
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

TEST_F(OTIOTrackTests, RangeTrimmedOutTest)
{
    RationalTime* start_time = RationalTime_create(60, 24);
    RationalTime* duration   = RationalTime_create(10, 24);
    TimeRange*    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Track* sq = Track_create("top_track", source_range, NULL, NULL);
    TimeRange_destroy(source_range);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    start_time = RationalTime_create(100, 24);
    duration   = RationalTime_create(50, 24);
    TimeRange* st_sourcerange =
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

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    bool appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) clip1, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) clip2, errorStatus);
    ASSERT_TRUE(appendOK);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();
    /** should be trimmed out, at the moment, the sentinel for that is None */
    TimeRange* trimmed_range_of_child_index =
        Track_trimmed_range_of_child_at_index(sq, 0, errorStatus);
    EXPECT_EQ(OTIOErrorStatus_get_outcome(errorStatus), 21);
    TimeRange_destroy(trimmed_range_of_child_index);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();

    TimeRange* not_nothing =
        Track_trimmed_range_of_child_at_index(sq, 1, errorStatus);
    source_range = Item_source_range((Item*) sq);
    EXPECT_TRUE(TimeRange_equal(not_nothing, source_range));
    TimeRange_destroy(not_nothing);
    TimeRange_destroy(source_range);

    /** should trim out second clip */
    start_time = RationalTime_create(0, 24);
    duration   = RationalTime_create(10, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Item_set_source_range((Item*) sq, source_range);
    TimeRange_destroy(source_range);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();

    trimmed_range_of_child_index =
        Track_trimmed_range_of_child_at_index(sq, 1, errorStatus);
    EXPECT_EQ(OTIOErrorStatus_get_outcome(errorStatus), 21);
    TimeRange_destroy(trimmed_range_of_child_index);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();

    not_nothing  = Track_trimmed_range_of_child_at_index(sq, 0, errorStatus);
    source_range = Item_source_range((Item*) sq);
    EXPECT_TRUE(TimeRange_equal(not_nothing, source_range));
    TimeRange_destroy(not_nothing);
    TimeRange_destroy(source_range);

    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOTrackTests, RangeNestedTest)
{
    Track*        sq         = Track_create("inner", NULL, NULL, NULL);
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

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) sq);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 3);
    ComposableRetainerVector_destroy(composableRetainerVector);

    //    OTIOErrorStatus_destroy(errorStatus);
    //    errorStatus = OTIOErrorStatus_create();
    //    Track* sq2  = (Track*) SerializableObject_clone(
    //        (SerializableObject*) sq, errorStatus);
    //    printf("%d\n", OTIOErrorStatus_get_outcome(errorStatus));
    //    Track* sq3 = (Track*) SerializableObject_clone( //TODO fix segfault
    //        (SerializableObject*) sq, errorStatus);
    //    printf("%d\n", OTIOErrorStatus_get_outcome(errorStatus));
}

TEST_F(OTIOTrackTests, SetItemTest)
{
    Track*           sq          = Track_create(NULL, NULL, NULL, NULL);
    Clip*            it          = Clip_create(NULL, NULL, NULL, NULL);
    Clip*            it_2        = Clip_create(NULL, NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool             appendOK    = Composition_append_child(
        (Composition*) sq, (Composable*) it, errorStatus);
    ASSERT_TRUE(appendOK);
    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) sq);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 1);
    ComposableRetainerVector_destroy(composableRetainerVector);

    bool setOK = Composition_set_child(
        (Composition*) sq, 0, (Composable*) it_2, errorStatus);
    ASSERT_TRUE(setOK);
    composableRetainerVector = Composition_children((Composition*) sq);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 1);
    ComposableRetainerVector_destroy(composableRetainerVector);
    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
}

TEST_F(OTIOTrackTests, TransformedTimeTest)
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

    start_time = RationalTime_create(0, 24);
    duration   = RationalTime_create(50, 24);
    TimeRange* source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Gap* fl =
        Gap_create_with_source_range(source_range, "GAP", NULL, NULL, NULL);
    EXPECT_FALSE(Gap_visible(fl));

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) sq);
    RetainerComposable* retainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 0);
    Composable* retainerComposableValue =
        RetainerComposable_take_value(retainerComposable);
    clip1 = (Clip*) retainerComposableValue;
    EXPECT_STREQ(
        "clip1",
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) clip1));
    retainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 1);
    retainerComposableValue = RetainerComposable_take_value(retainerComposable);
    clip2                   = (Clip*) retainerComposableValue;
    EXPECT_STREQ(
        "clip2",
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) clip2));
    retainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 2);
    retainerComposableValue = RetainerComposable_take_value(retainerComposable);
    clip3                   = (Clip*) retainerComposableValue;
    EXPECT_STREQ(
        "clip3",
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) clip3));
    ComposableRetainerVector_destroy(composableRetainerVector);

    RationalTime* rationalTime     = RationalTime_create(0, 24);
    RationalTime* transformed_time = Item_transformed_time(
        (Item*) sq, rationalTime, (Item*) clip1, errorStatus);
    RationalTime* compare_time = RationalTime_create(100, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(0, 24);
    transformed_time = Item_transformed_time(
        (Item*) sq, rationalTime, (Item*) clip2, errorStatus);
    compare_time = RationalTime_create(51, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(0, 24);
    transformed_time = Item_transformed_time(
        (Item*) sq, rationalTime, (Item*) clip3, errorStatus);
    compare_time = RationalTime_create(2, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(50, 24);
    transformed_time = Item_transformed_time(
        (Item*) sq, rationalTime, (Item*) clip1, errorStatus);
    compare_time = RationalTime_create(150, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(50, 24);
    transformed_time = Item_transformed_time(
        (Item*) sq, rationalTime, (Item*) clip2, errorStatus);
    compare_time = RationalTime_create(101, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(50, 24);
    transformed_time = Item_transformed_time(
        (Item*) sq, rationalTime, (Item*) clip3, errorStatus);
    compare_time = RationalTime_create(52, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(100, 24);
    transformed_time = Item_transformed_time(
        (Item*) clip1, rationalTime, (Item*) sq, errorStatus);
    compare_time = RationalTime_create(0, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(101, 24);
    transformed_time = Item_transformed_time(
        (Item*) clip2, rationalTime, (Item*) sq, errorStatus);
    compare_time = RationalTime_create(50, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(102, 24);
    transformed_time = Item_transformed_time(
        (Item*) clip3, rationalTime, (Item*) sq, errorStatus);
    compare_time = RationalTime_create(100, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(150, 24);
    transformed_time = Item_transformed_time(
        (Item*) clip1, rationalTime, (Item*) sq, errorStatus);
    compare_time = RationalTime_create(50, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(151, 24);
    transformed_time = Item_transformed_time(
        (Item*) clip2, rationalTime, (Item*) sq, errorStatus);
    compare_time = RationalTime_create(100, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    rationalTime     = RationalTime_create(152, 24);
    transformed_time = Item_transformed_time(
        (Item*) clip3, rationalTime, (Item*) sq, errorStatus);
    compare_time = RationalTime_create(150, 24);
    EXPECT_TRUE(RationalTime_equal(transformed_time, compare_time));
    RationalTime_destroy(rationalTime);
    RationalTime_destroy(transformed_time);
    RationalTime_destroy(compare_time);

    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
}

TEST_F(OTIOTrackTests, NeighborsOfSimpleTest)
{
    Track* sq = Track_create(NULL, NULL, NULL, NULL);

    RationalTime* in_offset  = RationalTime_create(10, 24);
    RationalTime* out_offset = RationalTime_create(10, 24);

    Transition* trans =
        Transition_create(NULL, NULL, in_offset, out_offset, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    bool appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) trans, errorStatus);
    ASSERT_TRUE(appendOK);

    /** neighbors of first transition */
    RetainerPairComposable* neighbors = Track_neighbors_of(
        sq,
        (Composable*) trans,
        errorStatus,
        OTIO_Track_NeighbourGapPolicy_never);
    RetainerComposable* retainerComposable =
        RetainerPairComposable_first(neighbors);
    Composable* retainerComposableValue =
        RetainerComposable_take_value(retainerComposable);
    EXPECT_EQ(retainerComposableValue, nullptr);
    retainerComposable      = RetainerPairComposable_second(neighbors);
    retainerComposableValue = RetainerComposable_take_value(retainerComposable);
    EXPECT_EQ(retainerComposableValue, nullptr);

    /** test with the neighbor filling policy on */
    neighbors = Track_neighbors_of(
        sq,
        (Composable*) trans,
        errorStatus,
        OTIO_Track_NeighbourGapPolicy_around_transitions);
    RationalTime* start_time = RationalTime_create(0, 24);
    TimeRange*    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, in_offset);
    Gap* fill =
        Gap_create_with_source_range(source_range, NULL, NULL, NULL, NULL);
    retainerComposable      = RetainerPairComposable_first(neighbors);
    retainerComposableValue = RetainerComposable_take_value(retainerComposable);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) retainerComposableValue,
        (SerializableObject*) fill));
    retainerComposable      = RetainerPairComposable_second(neighbors);
    retainerComposableValue = RetainerComposable_take_value(retainerComposable);
    //    EXPECT_TRUE(SerializableObject_is_equivalent_to( //TODO fix segfault
    //        (SerializableObject*) retainerComposableValue,
    //        (SerializableObject*) fill));

    SerializableObject_possibly_delete((SerializableObject*) sq);
    sq = NULL;
}

TEST_F(OTIOTrackTests, NeighborsOfFromDataTest)
{
    const char* edl_file = "transition_test.otio";
    char*       edl_path = (char*) calloc(
        strlen(sample_data_dir) + strlen(edl_file) + 1, sizeof(char));
    strcpy(edl_path, sample_data_dir);
    strcat(edl_path, edl_file);

    Timeline*        timeline    = Timeline_create(NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Any*             timelineAny = create_safely_typed_any_serializable_object(
        (SerializableObject*) timeline);
    bool deserializeOK =
        deserialize_json_from_file(edl_path, timelineAny, errorStatus);
    ASSERT_TRUE(deserializeOK);

    timeline = (Timeline*) safely_cast_retainer_any(timelineAny);

    Stack* stack = Timeline_tracks(timeline);

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) stack);
    RetainerComposable* firstTrackRetainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 0);

    Track* seq =
        (Track*) RetainerComposable_take_value(firstTrackRetainerComposable);

    ComposableRetainerVector_destroy(composableRetainerVector);
    composableRetainerVector = NULL;

    composableRetainerVector = Composition_children((Composition*) seq);
    RetainerComposable* seq_0_retainer =
        ComposableRetainerVector_at(composableRetainerVector, 0);
    RetainerComposable* seq_1_retainer =
        ComposableRetainerVector_at(composableRetainerVector, 1);
    RetainerComposable* seq_2_retainer =
        ComposableRetainerVector_at(composableRetainerVector, 2);
    RetainerComposable* seq_3_retainer =
        ComposableRetainerVector_at(composableRetainerVector, 3);
    RetainerComposable* seq_4_retainer =
        ComposableRetainerVector_at(composableRetainerVector, 4);
    RetainerComposable* seq_5_retainer =
        ComposableRetainerVector_at(composableRetainerVector, 5);
    Composable* seq_0 = RetainerComposable_take_value(seq_0_retainer);
    Composable* seq_1 = RetainerComposable_take_value(seq_1_retainer);
    Composable* seq_2 = RetainerComposable_take_value(seq_2_retainer);
    Composable* seq_3 = RetainerComposable_take_value(seq_3_retainer);
    Composable* seq_4 = RetainerComposable_take_value(seq_4_retainer);
    Composable* seq_5 = RetainerComposable_take_value(seq_5_retainer);
    RetainerPairComposable* neighbors = Track_neighbors_of(
        seq, seq_0, errorStatus, OTIO_Track_NeighbourGapPolicy_never);
    RetainerComposable* firstRetainerComposable =
        RetainerPairComposable_first(neighbors);
    RetainerComposable* secondRetainerComposable =
        RetainerPairComposable_second(neighbors);
    Composable* firstComposable =
        RetainerComposable_take_value(firstRetainerComposable);
    Composable* secondComposable =
        RetainerComposable_take_value(secondRetainerComposable);
    EXPECT_EQ(firstComposable, nullptr);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) secondComposable, (SerializableObject*) seq_1));

    RetainerPairComposable_destroy(neighbors);

    RationalTime* seq_0_in_offset = Transition_in_offset((Transition*) seq_0);
    RationalTime* start_time =
        RationalTime_create(0, RationalTime_rate(seq_0_in_offset));
    TimeRange* source_range = TimeRange_create_with_start_time_and_duration(
        start_time, seq_0_in_offset);
    Gap* fill =
        Gap_create_with_source_range(source_range, NULL, NULL, NULL, NULL);
    neighbors = Track_neighbors_of(
        seq,
        seq_0,
        errorStatus,
        OTIO_Track_NeighbourGapPolicy_around_transitions);
    firstRetainerComposable  = RetainerPairComposable_first(neighbors);
    secondRetainerComposable = RetainerPairComposable_second(neighbors);
    firstComposable  = RetainerComposable_take_value(firstRetainerComposable);
    secondComposable = RetainerComposable_take_value(secondRetainerComposable);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) firstComposable, (SerializableObject*) fill));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) secondComposable, (SerializableObject*) seq_1));
    RationalTime_destroy(seq_0_in_offset);
    RationalTime_destroy(start_time);
    TimeRange_destroy(source_range);
    RetainerPairComposable_destroy(neighbors);

    /** neighbor around second transition */
    neighbors = Track_neighbors_of(
        seq, seq_2, errorStatus, OTIO_Track_NeighbourGapPolicy_never);
    firstRetainerComposable  = RetainerPairComposable_first(neighbors);
    secondRetainerComposable = RetainerPairComposable_second(neighbors);
    firstComposable  = RetainerComposable_take_value(firstRetainerComposable);
    secondComposable = RetainerComposable_take_value(secondRetainerComposable);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) firstComposable, (SerializableObject*) seq_1));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) secondComposable, (SerializableObject*) seq_3));

    RetainerPairComposable_destroy(neighbors);

    /** no change w/ different policy */
    neighbors = Track_neighbors_of(
        seq,
        seq_2,
        errorStatus,
        OTIO_Track_NeighbourGapPolicy_around_transitions);
    firstRetainerComposable  = RetainerPairComposable_first(neighbors);
    secondRetainerComposable = RetainerPairComposable_second(neighbors);
    firstComposable  = RetainerComposable_take_value(firstRetainerComposable);
    secondComposable = RetainerComposable_take_value(secondRetainerComposable);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) firstComposable, (SerializableObject*) seq_1));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) secondComposable, (SerializableObject*) seq_3));

    RetainerPairComposable_destroy(neighbors);

    /** neighbor around third transition */
    neighbors = Track_neighbors_of(
        seq, seq_5, errorStatus, OTIO_Track_NeighbourGapPolicy_never);
    firstRetainerComposable  = RetainerPairComposable_first(neighbors);
    secondRetainerComposable = RetainerPairComposable_second(neighbors);
    firstComposable  = RetainerComposable_take_value(firstRetainerComposable);
    secondComposable = RetainerComposable_take_value(secondRetainerComposable);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) firstComposable, (SerializableObject*) seq_4));
    EXPECT_EQ(secondComposable, nullptr);

    RetainerPairComposable_destroy(neighbors);

    RationalTime* seq_5_out_offset = Transition_out_offset((Transition*) seq_5);
    start_time   = RationalTime_create(0, RationalTime_rate(seq_5_out_offset));
    source_range = TimeRange_create_with_start_time_and_duration(
        start_time, seq_5_out_offset);
    fill = Gap_create_with_source_range(source_range, NULL, NULL, NULL, NULL);
    neighbors = Track_neighbors_of(
        seq,
        seq_5,
        errorStatus,
        OTIO_Track_NeighbourGapPolicy_around_transitions);
    firstRetainerComposable  = RetainerPairComposable_first(neighbors);
    secondRetainerComposable = RetainerPairComposable_second(neighbors);
    firstComposable  = RetainerComposable_take_value(firstRetainerComposable);
    secondComposable = RetainerComposable_take_value(secondRetainerComposable);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) firstComposable, (SerializableObject*) seq_4));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) secondComposable, (SerializableObject*) fill));
    RationalTime_destroy(seq_5_out_offset);
    RationalTime_destroy(start_time);
    TimeRange_destroy(source_range);
    RetainerPairComposable_destroy(neighbors);

    SerializableObject_possibly_delete((SerializableObject*) seq);
    seq = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOTrackTests, TrackRangeOfAllChildrenTest)
{
    const char* edl_file = "transition_test.otio";
    char*       edl_path = (char*) calloc(
        strlen(sample_data_dir) + strlen(edl_file) + 1, sizeof(char));
    strcpy(edl_path, sample_data_dir);
    strcat(edl_path, edl_file);

    Timeline*        timeline    = Timeline_create(NULL, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Any*             timelineAny = create_safely_typed_any_serializable_object(
        (SerializableObject*) timeline);
    bool deserializeOK =
        deserialize_json_from_file(edl_path, timelineAny, errorStatus);
    ASSERT_TRUE(deserializeOK);

    timeline = (Timeline*) safely_cast_retainer_any(timelineAny);

    Stack* stack = Timeline_tracks(timeline);

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) stack);
    RetainerComposable* firstTrackRetainerComposable =
        ComposableRetainerVector_at(composableRetainerVector, 0);

    Track* tr =
        (Track*) RetainerComposable_take_value(firstTrackRetainerComposable);

    MapComposableTimeRange* mp = Track_range_of_all_children(tr, errorStatus);

    /** fetch all the valid children that should be in the map */
    ComposableVector* vc = Track_each_clip(tr);

    Composable*                     vc_0 = ComposableVector_at(vc, 0);
    Composable*                     vc_1 = ComposableVector_at(vc, 1);
    MapComposableTimeRangeIterator* it = MapComposableTimeRange_find(mp, vc_0);
    TimeRange* mp_vc_0 = MapComposableTimeRangeIterator_value(it);
    MapComposableTimeRangeIterator_destroy(it);
    it                 = MapComposableTimeRange_find(mp, vc_1);
    TimeRange* mp_vc_1 = MapComposableTimeRangeIterator_value(it);
    MapComposableTimeRangeIterator_destroy(it);
    RationalTime* mp_vc_0_start_time = TimeRange_start_time(mp_vc_0);
    RationalTime* mp_vc_0_duration   = TimeRange_duration(mp_vc_0);
    RationalTime* mp_vc_1_start_time = TimeRange_start_time(mp_vc_1);

    EXPECT_EQ(RationalTime_value(mp_vc_0_start_time), 0);
    EXPECT_TRUE(RationalTime_equal(mp_vc_1_start_time, mp_vc_0_duration));
    RationalTime_destroy(mp_vc_0_duration);
    RationalTime_destroy(mp_vc_0_start_time);
    RationalTime_destroy(mp_vc_1_start_time);
    TimeRange_destroy(mp_vc_1);
    TimeRange_destroy(mp_vc_0);
    ComposableVector_destroy(vc);

    ComposableRetainerVector* timeline_tracks_retainer_vector =
        composableRetainerVector;
    //        Composition_children((Composition*) timeline);
    ComposableRetainerVectorIterator* it_tracks =
        ComposableRetainerVector_begin(timeline_tracks_retainer_vector);
    ComposableRetainerVectorIterator* it_tracks_end =
        ComposableRetainerVector_end(timeline_tracks_retainer_vector);
    for(; ComposableRetainerVectorIterator_not_equal(it_tracks, it_tracks_end);
        ComposableRetainerVectorIterator_advance(it_tracks, 1))
    {
        RetainerComposable* track_retainer =
            ComposableRetainerVectorIterator_value(it_tracks);
        Track* track = (Track*) RetainerComposable_value(track_retainer);

        ComposableRetainerVector* track_children_retainer_vector =
            Composition_children((Composition*) track);
        ComposableRetainerVectorIterator* it_track_children =
            ComposableRetainerVector_begin(track_children_retainer_vector);
        ComposableRetainerVectorIterator* it_track_children_end =
            ComposableRetainerVector_end(track_children_retainer_vector);
        for(; ComposableRetainerVectorIterator_not_equal(
                it_track_children, it_track_children_end);
            ComposableRetainerVectorIterator_advance(it_track_children, 1))
        {
            RetainerComposable* child_retainer =
                ComposableRetainerVectorIterator_value(it_track_children);
            Composable* child = RetainerComposable_value(child_retainer);

            TimeRange* child_range_in_parent =
                Item_range_in_parent((Item*) child, errorStatus);

            it                       = MapComposableTimeRange_find(mp, child);
            TimeRange* range_compare = MapComposableTimeRangeIterator_value(it);

            EXPECT_TRUE(TimeRange_equal(child_range_in_parent, range_compare));

            TimeRange_destroy(child_range_in_parent);
            child_range_in_parent = NULL;
            TimeRange_destroy(range_compare);
            range_compare = NULL;
            MapComposableTimeRangeIterator_destroy(it);
            it = NULL;
        }
        ComposableRetainerVector_destroy(track_children_retainer_vector);
        track_children_retainer_vector = NULL;
        ComposableRetainerVectorIterator_destroy(it_track_children);
        it_track_children = NULL;
        ComposableRetainerVectorIterator_destroy(it_track_children_end);
        it_track_children_end = NULL;
    }
    ComposableRetainerVector_destroy(timeline_tracks_retainer_vector);
    timeline_tracks_retainer_vector = NULL;
    ComposableRetainerVectorIterator_destroy(it_tracks);
    it_tracks = NULL;
    ComposableRetainerVectorIterator_destroy(it_tracks_end);
    it_tracks_end = NULL;
    MapComposableTimeRange_destroy(mp);
    mp = NULL;

    Track* track = Track_create(NULL, NULL, NULL, NULL);
    mp           = Track_range_of_all_children(track, errorStatus);
    EXPECT_EQ(MapComposableTimeRange_size(mp), 0);
    MapComposableTimeRange_destroy(mp);
    mp = NULL;
    SerializableObject_possibly_delete((SerializableObject*) track);
    track = NULL;

    SerializableObject_possibly_delete((SerializableObject*) timeline);
    timeline = NULL;
}

TEST_F(OTIOEdgeCases, EmptyCompositionsTest)
{
    Timeline*                 timeline = Timeline_create(NULL, NULL, NULL);
    Stack*                    stack    = Timeline_tracks(timeline);
    ComposableRetainerVector* children =
        Composition_children((Composition*) stack);
    EXPECT_EQ(ComposableRetainerVector_size(children), 0);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Stack*        tracks           = Timeline_tracks(timeline);
    RationalTime* duration         = Item_duration((Item*) tracks, errorStatus);
    RationalTime* duration_compare = RationalTime_create(0, 24);
    EXPECT_TRUE(RationalTime_equal(duration, duration_compare));

    RationalTime_destroy(duration);
    duration = NULL;
    RationalTime_destroy(duration_compare);
    duration_compare = NULL;
    ComposableRetainerVector_destroy(children);
    children = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    SerializableObject_possibly_delete((SerializableObject*) timeline);
    timeline = NULL;
}

TEST_F(OTIOEdgeCases, IteratingOverDupesTest)
{
    Timeline*        timeline    = Timeline_create(NULL, NULL, NULL);
    Track*           track       = Track_create(NULL, NULL, NULL, NULL);
    Stack*           stack       = Timeline_tracks(timeline);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    bool             appendOK    = Composition_append_child(
        (Composition*) stack, (Composable*) track, errorStatus);
    ASSERT_TRUE(appendOK);

    RationalTime* start_time = RationalTime_create(10, 30);
    RationalTime* duration   = RationalTime_create(15, 30);
    TimeRange*    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    /** make several identical copies */
    for(int i = 0; i < 10; ++i)
    {
        Clip* clip = Clip_create("Dupe", NULL, source_range, NULL);
        appendOK   = Composition_append_child(
            (Composition*) track, (Composable*) clip, errorStatus);
        ASSERT_TRUE(appendOK);
    }

    ComposableRetainerVector* composableRetainerVector =
        Composition_children((Composition*) track);
    EXPECT_EQ(ComposableRetainerVector_size(composableRetainerVector), 10);

    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);

    start_time = RationalTime_create(0, 30);
    duration   = RationalTime_create(150, 30);
    TimeRange* range_compare =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    TimeRange* track_trimmed_range =
        Item_trimmed_range((Item*) track, errorStatus);
    EXPECT_TRUE(TimeRange_equal(range_compare, track_trimmed_range));
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(range_compare);
    TimeRange_destroy(track_trimmed_range);

    /** test normal iteration */
    TimeRange*                        previous = NULL;
    ComposableRetainerVectorIterator* it =
        ComposableRetainerVector_begin(composableRetainerVector);
    ComposableRetainerVectorIterator* it_end =
        ComposableRetainerVector_end(composableRetainerVector);
    for(; ComposableRetainerVectorIterator_not_equal(it, it_end);
        ComposableRetainerVectorIterator_advance(it, 1))
    {
        RetainerComposable* retainerComposable =
            ComposableRetainerVectorIterator_value(it);
        Composable* item = RetainerComposable_value(retainerComposable);

        TimeRange* range_of_child =
            Composition_range_of_child((Composition*) track, item, errorStatus);
        TimeRange* range_in_parent =
            Item_range_in_parent((Item*) item, errorStatus);

        EXPECT_TRUE(TimeRange_equal(range_of_child, range_in_parent));
        if(previous != NULL)
        {
            EXPECT_FALSE(TimeRange_equal(previous, range_in_parent));
            TimeRange_destroy(previous);
            previous = NULL;
        }

        previous = Item_range_in_parent((Item*) item, errorStatus);

        TimeRange_destroy(range_in_parent);
        TimeRange_destroy(range_of_child);
    }
    TimeRange_destroy(previous);
    previous = NULL;
    ComposableRetainerVectorIterator_destroy(it);
    it = NULL;
    ComposableRetainerVectorIterator_destroy(it_end);
    it_end = NULL;

    /** test recursive iteration */

    ComposableVector*         composableVector = Track_each_clip(track);
    ComposableVectorIterator* clip_it =
        ComposableVector_begin(composableVector);
    ComposableVectorIterator* clip_it_end =
        ComposableVector_end(composableVector);
    for(; ComposableVectorIterator_not_equal(clip_it, clip_it_end);
        ComposableVectorIterator_advance(clip_it, 1))
    {
        Composable* item = ComposableVectorIterator_value(clip_it);

        TimeRange* range_of_child =
            Composition_range_of_child((Composition*) track, item, errorStatus);
        TimeRange* range_in_parent =
            Item_range_in_parent((Item*) item, errorStatus);

        EXPECT_TRUE(TimeRange_equal(range_of_child, range_in_parent));
        if(previous != NULL)
        {
            EXPECT_FALSE(TimeRange_equal(previous, range_in_parent));
            TimeRange_destroy(previous);
            previous = NULL;
        }

        previous = Item_range_in_parent((Item*) item, errorStatus);

        TimeRange_destroy(range_in_parent);
        TimeRange_destroy(range_of_child);
    }
    TimeRange_destroy(previous);
    previous = NULL;
    ComposableVectorIterator_destroy(clip_it);
    clip_it = NULL;
    ComposableVectorIterator_destroy(clip_it_end);
    clip_it_end = NULL;

    /** compare to iteration by index */
    it     = ComposableRetainerVector_begin(composableRetainerVector);
    it_end = ComposableRetainerVector_end(composableRetainerVector);
    int i  = 0;
    for(; ComposableRetainerVectorIterator_not_equal(it, it_end);
        ComposableRetainerVectorIterator_advance(it, 1), i++)
    {
        RetainerComposable* retainerComposable =
            ComposableRetainerVectorIterator_value(it);
        Composable* item = RetainerComposable_value(retainerComposable);

        TimeRange* range_of_child =
            Composition_range_of_child((Composition*) track, item, errorStatus);
        TimeRange* range_in_parent =
            Item_range_in_parent((Item*) item, errorStatus);
        TimeRange* range_of_child_index =
            Track_range_of_child_at_index(track, i, errorStatus);

        EXPECT_TRUE(TimeRange_equal(range_of_child, range_in_parent));
        EXPECT_TRUE(TimeRange_equal(range_of_child, range_of_child_index));
        if(previous != NULL)
        {
            EXPECT_FALSE(TimeRange_equal(previous, range_in_parent));
            TimeRange_destroy(previous);
            previous = NULL;
        }

        previous = Item_range_in_parent((Item*) item, errorStatus);

        TimeRange_destroy(range_in_parent);
        TimeRange_destroy(range_of_child);
        TimeRange_destroy(range_of_child_index);
    }
    TimeRange_destroy(previous);
    previous = NULL;
    ComposableRetainerVectorIterator_destroy(it);
    it = NULL;
    ComposableRetainerVectorIterator_destroy(it_end);
    it_end = NULL;
    i      = 0;

    /** compare recursive to iteration by index */
    composableVector = Track_each_clip(track);
    clip_it          = ComposableVector_begin(composableVector);
    clip_it_end      = ComposableVector_end(composableVector);
    for(; ComposableVectorIterator_not_equal(clip_it, clip_it_end);
        ComposableVectorIterator_advance(clip_it, 1), i++)
    {
        Composable* item = ComposableVectorIterator_value(clip_it);

        TimeRange* range_of_child =
            Composition_range_of_child((Composition*) track, item, errorStatus);
        TimeRange* range_in_parent =
            Item_range_in_parent((Item*) item, errorStatus);
        TimeRange* range_of_child_index =
            Track_range_of_child_at_index(track, i, errorStatus);

        EXPECT_TRUE(TimeRange_equal(range_of_child, range_in_parent));
        EXPECT_TRUE(TimeRange_equal(range_of_child, range_of_child_index));
        if(previous != NULL)
        {
            EXPECT_FALSE(TimeRange_equal(previous, range_in_parent));
            TimeRange_destroy(previous);
            previous = NULL;
        }

        previous = Item_range_in_parent((Item*) item, errorStatus);

        TimeRange_destroy(range_in_parent);
        TimeRange_destroy(range_of_child);
        TimeRange_destroy(range_of_child_index);
    }
    TimeRange_destroy(previous);
    previous = NULL;
    ComposableVectorIterator_destroy(clip_it);
    clip_it = NULL;
    ComposableVectorIterator_destroy(clip_it_end);
    clip_it_end = NULL;

    ComposableRetainerVector_destroy(composableRetainerVector);
    composableRetainerVector = NULL;
    ComposableVector_destroy(composableVector);
    composableVector = NULL;
    SerializableObject_possibly_delete((SerializableObject*) timeline);
    timeline = NULL;
}

TEST_F(OTIONestingTest, DeeplyNestedTest)
{
    /**
     * Take a single clip of media (frames 100-200) and nest it into a bunch
     * of layers
     * Nesting it should not shift the media at all.
     * At one level:
     * Timeline:
     *   Stack: [0-99]
     *    Track: [0-99]
     *     Clip: [100-199]
     *      Media Reference: [100-199]
     */

    /** here are some times in the top-level coordinate system */
    RationalTime* zero       = RationalTime_create(0, 24);
    RationalTime* one        = RationalTime_create(1, 24);
    RationalTime* fifty      = RationalTime_create(50, 24);
    RationalTime* ninetynine = RationalTime_create(99, 24);
    RationalTime* onehundred = RationalTime_create(100, 24);
    TimeRange*    top_level_range =
        TimeRange_create_with_start_time_and_duration(zero, onehundred);

    /** here are some times in the media-level coordinate system */
    RationalTime* first_frame = RationalTime_create(100, 24);
    RationalTime* middle      = RationalTime_create(150, 24);
    RationalTime* last        = RationalTime_create(199, 24);
    TimeRange*    media_range =
        TimeRange_create_with_start_time_and_duration(first_frame, onehundred);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Timeline*         timeline = Timeline_create(NULL, NULL, NULL);
    Stack*            stack    = Timeline_tracks(timeline);
    Track*            track    = Track_create(NULL, NULL, NULL, NULL);
    Clip*             clip     = Clip_create(NULL, NULL, NULL, NULL);
    MissingReference* media = MissingReference_create(NULL, media_range, NULL);
    Clip_set_media_reference(clip, (MediaReference*) media);
    bool appendOK = Composition_append_child(
        (Composition*) track, (Composable*) clip, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) stack, (Composable*) track, errorStatus);
    ASSERT_TRUE(appendOK);

    Composition* clip_parent  = Composable_parent((Composable*) clip);
    Composition* track_parent = Composable_parent((Composable*) track);

    EXPECT_EQ(track, (Track*) clip_parent);
    EXPECT_EQ(stack, (Stack*) track_parent);

    /**
     * the clip and track should auto-size to fit the media, since we
     * haven't trimmed anything
     */
    RationalTime* clip_duration  = Item_duration((Item*) clip, errorStatus);
    RationalTime* stack_duration = Item_duration((Item*) stack, errorStatus);
    RationalTime* track_duration = Item_duration((Item*) track, errorStatus);
    EXPECT_TRUE(RationalTime_equal(clip_duration, onehundred));
    EXPECT_TRUE(RationalTime_equal(stack_duration, onehundred));
    EXPECT_TRUE(RationalTime_equal(track_duration, onehundred));
    RationalTime_destroy(clip_duration);
    clip_duration = NULL;
    RationalTime_destroy(stack_duration);
    stack_duration = NULL;
    RationalTime_destroy(track_duration);
    track_duration = NULL;

    /** the ranges should match our expectations... */
    TimeRange* clip_trimmed_range =
        Item_trimmed_range((Item*) clip, errorStatus);
    TimeRange* stack_trimmed_range =
        Item_trimmed_range((Item*) stack, errorStatus);
    TimeRange* track_trimmed_range =
        Item_trimmed_range((Item*) track, errorStatus);
    EXPECT_TRUE(TimeRange_equal(clip_trimmed_range, media_range));
    EXPECT_TRUE(TimeRange_equal(stack_trimmed_range, top_level_range));
    EXPECT_TRUE(TimeRange_equal(track_trimmed_range, top_level_range));
    TimeRange_destroy(clip_trimmed_range);
    clip_trimmed_range = NULL;
    TimeRange_destroy(stack_trimmed_range);
    stack_trimmed_range = NULL;
    TimeRange_destroy(track_trimmed_range);
    track_trimmed_range = NULL;

    /** verify that the media is where we expect */
    RationalTime* stack_transformed_time_zero_clip =
        Item_transformed_time((Item*) stack, zero, (Item*) clip, errorStatus);
    RationalTime* stack_transformed_time_fifty_clip =
        Item_transformed_time((Item*) stack, fifty, (Item*) clip, errorStatus);
    RationalTime* stack_transformed_time_ninetynine_clip =
        Item_transformed_time(
            (Item*) stack, ninetynine, (Item*) clip, errorStatus);
    EXPECT_TRUE(
        RationalTime_equal(stack_transformed_time_zero_clip, first_frame));
    EXPECT_TRUE(RationalTime_equal(stack_transformed_time_fifty_clip, middle));
    EXPECT_TRUE(
        RationalTime_equal(stack_transformed_time_ninetynine_clip, last));
    RationalTime_destroy(stack_transformed_time_zero_clip);
    stack_transformed_time_zero_clip = NULL;
    RationalTime_destroy(stack_transformed_time_fifty_clip);
    stack_transformed_time_fifty_clip = NULL;
    RationalTime_destroy(stack_transformed_time_ninetynine_clip);
    stack_transformed_time_ninetynine_clip = NULL;

    int             num_wrappers = 10;
    Stack*          wrappers[num_wrappers];
    ClipWrapperPair clipWrapperPair;
    clipWrapperPair.clip = clip;
    for(int i = 0; i < num_wrappers; ++i)
    {
        //        Stack* wrapper = _nest(clip, 0);
        clipWrapperPair = _nest(clipWrapperPair.clip, 0);
        wrappers[i]     = clipWrapperPair.wrapper;
        clip            = clipWrapperPair.clip;
    }
    /* nothing should have shifted at all */

    /*const char* encoded = serialize_json_to_string(
        create_safely_typed_any_serializable_object(
            (SerializableObject*) timeline),
        errorStatus,
        4);
    printf("%s\n", encoded);*/

    /**
     * the clip and track should auto-size to fit the media, since we
     * haven't trimmed anything
     */
    clip_duration  = Item_duration((Item*) clip, errorStatus);
    stack_duration = Item_duration((Item*) stack, errorStatus);
    track_duration = Item_duration((Item*) track, errorStatus);
    EXPECT_TRUE(RationalTime_equal(clip_duration, onehundred));
    EXPECT_TRUE(RationalTime_equal(stack_duration, onehundred));
    EXPECT_TRUE(RationalTime_equal(track_duration, onehundred));
    RationalTime_destroy(clip_duration);
    clip_duration = NULL;
    RationalTime_destroy(stack_duration);
    stack_duration = NULL;
    RationalTime_destroy(track_duration);
    track_duration = NULL;

    /** the ranges should match our expectations... */
    clip_trimmed_range  = Item_trimmed_range((Item*) clip, errorStatus);
    stack_trimmed_range = Item_trimmed_range((Item*) stack, errorStatus);
    track_trimmed_range = Item_trimmed_range((Item*) track, errorStatus);
    EXPECT_TRUE(TimeRange_equal(clip_trimmed_range, media_range));
    EXPECT_TRUE(TimeRange_equal(stack_trimmed_range, top_level_range));
    EXPECT_TRUE(TimeRange_equal(track_trimmed_range, top_level_range));
    TimeRange_destroy(clip_trimmed_range);
    clip_trimmed_range = NULL;
    TimeRange_destroy(stack_trimmed_range);
    stack_trimmed_range = NULL;
    TimeRange_destroy(track_trimmed_range);
    track_trimmed_range = NULL;

    /** verify that the media is where we expect */
    stack_transformed_time_zero_clip =
        Item_transformed_time((Item*) stack, zero, (Item*) clip, errorStatus);
    stack_transformed_time_fifty_clip =
        Item_transformed_time((Item*) stack, fifty, (Item*) clip, errorStatus);
    stack_transformed_time_ninetynine_clip = Item_transformed_time(
        (Item*) stack, ninetynine, (Item*) clip, errorStatus);
    EXPECT_TRUE(
        RationalTime_equal(stack_transformed_time_zero_clip, first_frame));
    EXPECT_TRUE(RationalTime_equal(stack_transformed_time_fifty_clip, middle));
    EXPECT_TRUE(
        RationalTime_equal(stack_transformed_time_ninetynine_clip, last));
    RationalTime_destroy(stack_transformed_time_zero_clip);
    stack_transformed_time_zero_clip = NULL;
    RationalTime_destroy(stack_transformed_time_fifty_clip);
    stack_transformed_time_fifty_clip = NULL;
    RationalTime_destroy(stack_transformed_time_ninetynine_clip);
    stack_transformed_time_ninetynine_clip = NULL;

    /** now trim them all by one frame at each end */
    RationalTime* duration = RationalTime_subtract(ninetynine, one);
    TimeRange*    trim =
        TimeRange_create_with_start_time_and_duration(one, duration);
    RationalTime* time_compare  = RationalTime_create(98, 24);
    RationalTime* trim_duration = TimeRange_duration(trim);
    EXPECT_TRUE(RationalTime_equal(time_compare, trim_duration));
    RationalTime_destroy(duration);
    duration = NULL;
    RationalTime_destroy(trim_duration);
    trim_duration = NULL;

    for(int j = 0; j < num_wrappers; ++j)
    {
        Item_set_source_range((Item*) wrappers[j], trim);
    }

    /*const char* encoded = serialize_json_to_string(
        create_safely_typed_any_serializable_object(
            (SerializableObject*) timeline),
        errorStatus,
        4);
    printf("%s\n", encoded);*/

    /** the clip should be the same */
    clip_duration = Item_duration((Item*) clip, errorStatus);
    EXPECT_TRUE(RationalTime_equal(clip_duration, onehundred));
    RationalTime_destroy(clip_duration);
    clip_duration = NULL;

    /** the parents should have shrunk by only 2 frames */

    track_duration = Item_duration((Item*) track, errorStatus);
    stack_duration = Item_duration((Item*) stack, errorStatus);
    EXPECT_TRUE(RationalTime_equal(track_duration, time_compare));
    EXPECT_TRUE(RationalTime_equal(stack_duration, time_compare));
    RationalTime_destroy(time_compare);
    time_compare = NULL;
    RationalTime_destroy(track_duration);
    track_duration = NULL;
    RationalTime_destroy(stack_duration);
    stack_duration = NULL;

    /**
     * but the media should have shifted over by 1 one frame for each level
     * of nesting
     */

    RationalTime* ten = RationalTime_create(num_wrappers, 24);
    stack_transformed_time_zero_clip =
        Item_transformed_time((Item*) stack, zero, (Item*) clip, errorStatus);
    stack_transformed_time_fifty_clip =
        Item_transformed_time((Item*) stack, fifty, (Item*) clip, errorStatus);
    stack_transformed_time_ninetynine_clip = Item_transformed_time(
        (Item*) stack, ninetynine, (Item*) clip, errorStatus);
    RationalTime* first_frame_plus_ten = RationalTime_add(first_frame, ten);
    RationalTime* middle_plus_ten      = RationalTime_add(middle, ten);
    RationalTime* last_plus_ten        = RationalTime_add(last, ten);
    EXPECT_TRUE(RationalTime_equal(
        stack_transformed_time_zero_clip, first_frame_plus_ten));
    EXPECT_TRUE(
        RationalTime_equal(stack_transformed_time_fifty_clip, middle_plus_ten));
    EXPECT_TRUE(RationalTime_equal(
        stack_transformed_time_ninetynine_clip, last_plus_ten));
    RationalTime_destroy(ten);
    ten = NULL;
    RationalTime_destroy(stack_transformed_time_zero_clip);
    stack_transformed_time_zero_clip = NULL;
    RationalTime_destroy(stack_transformed_time_fifty_clip);
    stack_transformed_time_fifty_clip = NULL;
    RationalTime_destroy(stack_transformed_time_ninetynine_clip);
    stack_transformed_time_ninetynine_clip = NULL;
    RationalTime_destroy(first_frame_plus_ten);
    first_frame_plus_ten = NULL;
    RationalTime_destroy(middle_plus_ten);
    middle_plus_ten = NULL;
    RationalTime_destroy(last_plus_ten);
    last_plus_ten = NULL;

    SerializableObject_possibly_delete((SerializableObject*) timeline);
    timeline = NULL;
}

TEST_F(OTIONestingTest, ChildAtTimeWithChildrenTest)
{
    Track* sq = Track_create("foo", NULL, NULL, NULL);

    RationalTime* start_time = RationalTime_create(9, 24);
    RationalTime* duration   = RationalTime_create(12, 24);
    TimeRange*    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);

    Track* body = Track_create("body", source_range, NULL, NULL);

    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);

    start_time = RationalTime_create(100, 24);
    duration   = RationalTime_create(10, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip1 = Clip_create("clip1", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);
    start_time = RationalTime_create(101, 24);
    duration   = RationalTime_create(10, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip2 = Clip_create("clip2", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);
    start_time = RationalTime_create(102, 24);
    duration   = RationalTime_create(10, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* clip3 = Clip_create("clip3", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    bool appendOK = Composition_append_child(
        (Composition*) body, (Composable*) clip1, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) body, (Composable*) clip2, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) body, (Composable*) clip3, errorStatus);
    ASSERT_TRUE(appendOK);

    start_time = RationalTime_create(100, 24);
    duration   = RationalTime_create(10, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* leader = Clip_create("leader", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);

    start_time = RationalTime_create(102, 24);
    duration   = RationalTime_create(10, 24);
    source_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);
    Clip* credits = Clip_create("credits", NULL, source_range, NULL);
    RationalTime_destroy(start_time);
    RationalTime_destroy(duration);
    TimeRange_destroy(source_range);

    appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) leader, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) body, errorStatus);
    ASSERT_TRUE(appendOK);
    appendOK = Composition_append_child(
        (Composition*) sq, (Composable*) credits, errorStatus);
    ASSERT_TRUE(appendOK);

    /**
     * Looks like this:
     * [ leader ][ body ][ credits ]
     * 10 f       12f     10f
     *
     * body: (source range starts: 9f duration: 12f)
     * [ clip1 ][ clip2 ][ clip 3]
     * 1f       11f
     */

    
}