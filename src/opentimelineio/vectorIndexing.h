#pragma once

template <typename V>
inline int adjusted_vector_index(int index, V const& vec) {
    return index < 0 ? int(vec.size()) + index : index;
}
