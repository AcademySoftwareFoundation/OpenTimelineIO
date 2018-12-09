#ifndef OTIO_VECTOR_INDEXING_H
#define OTIO_VECTOR_INDEXING_H

template <typename V>
inline int adjusted_vector_index(int index, V const& vec) {
    return index < 0 ? int(vec.size()) + index : index;
}

#endif
