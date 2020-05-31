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
    void        SetUp() override { sample_data_dir = xstr(SAMPLE_DATA_DIR); }
    void        TearDown() override {}
    const char* sample_data_dir;
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