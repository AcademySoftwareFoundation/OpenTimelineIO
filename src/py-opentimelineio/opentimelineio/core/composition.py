from . _core_utils import add_method
from .. import _otio


@add_method(_otio.Composition)
def __str__(self):
    return "{}({}, {}, {}, {})".format(
        self.__class__.__name__,
        str(self.name),
        str(list(self)),
        str(self.source_range),
        str(self.metadata)
    )


@add_method(_otio.Composition)
def __repr__(self):
    return (
        "otio.{}.{}("
        "name={}, "
        "children={}, "
        "source_range={}, "
        "metadata={}"
        ")".format(
            "core" if self.__class__ is _otio.Composition else "schema",
            self.__class__.__name__,
            repr(self.name),
            repr(list(self)),
            repr(self.source_range),
            repr(self.metadata)
        )
    )


@add_method(_otio.Composition)
def child_at_time(
        self,
        search_time,
        shallow_search=False,
):
    """Return the child that overlaps with time search_time.

    search_time is in the space of self.

    If shallow_search is false, will recurse into compositions.
    """

    range_map = self.range_of_all_children()

    # find the first item whose end_time_exclusive is after the
    first_inside_range = _bisect_left(
        seq=self,
        tgt=search_time,
        key_func=lambda child: range_map[child].end_time_exclusive(),
    )

    # find the last item whose start_time is before the
    last_in_range = _bisect_right(
        seq=self,
        tgt=search_time,
        key_func=lambda child: range_map[child].start_time,
        lower_search_bound=first_inside_range,
    )

    # limit the search to children who are in the search_range
    possible_matches = self[first_inside_range:last_in_range]

    result = None
    for thing in possible_matches:
        if range_map[thing].overlaps(search_time):
            result = thing
            break

    # if the search cannot or should not continue
    if (
            result is None
            or shallow_search
            or not hasattr(result, "child_at_time")
    ):
        return result

    # before you recurse, you have to transform the time into the
    # space of the child
    child_search_time = self.transformed_time(search_time, result)

    return result.child_at_time(child_search_time, shallow_search)


@add_method(_otio.Composition)
def each_child(
        self,
        search_range=None,
        descended_from_type=_otio.Composable,
        shallow_search=False,
):
    """ Generator that returns each child contained in the composition in
    the order in which it is found.

    Arguments:
        search_range: if specified, only children whose range overlaps with
                      the search range will be yielded.
        descended_from_type: if specified, only children who are a
                      descendent of the descended_from_type will be yielded.
        shallow_search: if True, will only search children of self, not
                        and not recurse into children of children.
    """
    if search_range:
        range_map = self.range_of_all_children()

        # find the first item whose end_time_inclusive is after the
        # start_time of the search range
        first_inside_range = _bisect_left(
            seq=self,
            tgt=search_range.start_time,
            key_func=lambda child: range_map[child].end_time_inclusive(),
        )

        # find the last item whose start_time is before the
        # end_time_inclusive of the search_range
        last_in_range = _bisect_right(
            seq=self,
            tgt=search_range.end_time_inclusive(),
            key_func=lambda child: range_map[child].start_time,
            lower_search_bound=first_inside_range,
        )

        # limit the search to children who are in the search_range
        children = self[first_inside_range:last_in_range]
    else:
        # otherwise search all the children
        children = self

    for child in children:
        # filter out children who are not descended from the specified type
        # shortcut the isinstance if descended_from_type is composable
        # (since all objects in compositions are already composables)
        is_descendant = descended_from_type is _otio.Composable
        if is_descendant or isinstance(child, descended_from_type):
            yield child

        # if not a shallow_search, for children that are compositions,
        # recurse into their children
        if not shallow_search and hasattr(child, "each_child"):

            if search_range is not None:
                search_range = self.transformed_time_range(search_range, child)

            for valid_child in child.each_child(
                    search_range,
                    descended_from_type,
                    shallow_search
            ):
                yield valid_child


def _bisect_right(
        seq,
        tgt,
        key_func,
        lower_search_bound=0,
        upper_search_bound=None
):
    """Return the index of the last item in seq such that all e in seq[:index]
    have key_func(e) <= tgt, and all e in seq[index:] have key_func(e) > tgt.

    Thus, seq.insert(index, value) will insert value after the rightmost item
    such that meets the above condition.

    lower_search_bound and upper_search_bound bound the slice to be searched.

    Assumes that seq is already sorted.
    """

    if lower_search_bound < 0:
        raise ValueError('lower_search_bound must be non-negative')

    if upper_search_bound is None:
        upper_search_bound = len(seq)

    while lower_search_bound < upper_search_bound:
        midpoint_index = (lower_search_bound + upper_search_bound) // 2

        if tgt < key_func(seq[midpoint_index]):
            upper_search_bound = midpoint_index
        else:
            lower_search_bound = midpoint_index + 1

    return lower_search_bound


def _bisect_left(
        seq,
        tgt,
        key_func,
        lower_search_bound=0,
        upper_search_bound=None
):
    """Return the index of the last item in seq such that all e in seq[:index]
    have key_func(e) < tgt, and all e in seq[index:] have key_func(e) >= tgt.

    Thus, seq.insert(index, value) will insert value before the leftmost item
    such that meets the above condition.

    lower_search_bound and upper_search_bound bound the slice to be searched.

    Assumes that seq is already sorted.
    """

    if lower_search_bound < 0:
        raise ValueError('lower_search_bound must be non-negative')

    if upper_search_bound is None:
        upper_search_bound = len(seq)

    while lower_search_bound < upper_search_bound:
        midpoint_index = (lower_search_bound + upper_search_bound) // 2

        if key_func(seq[midpoint_index]) < tgt:
            lower_search_bound = midpoint_index + 1
        else:
            upper_search_bound = midpoint_index

    return lower_search_bound
