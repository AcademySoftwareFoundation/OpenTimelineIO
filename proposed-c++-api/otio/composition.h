#ifndef OTIO_COMPOSITION_H
#define OTIO_COMPOSITION_H

#include "item.h"

class Composition : public Item {
public:
    struct Schema {
        static auto constexpr name = "Composition";
        static int constexpr version = 1;
    };

    using Parent = Item;

    Composition(std::string const& name = std::string(),
                optional<TimeRange> const& source_range = nullopt,
                AnyDictionary const& metadata = AnyDictionary());

    virtual std::string& composition_kind() const;

    std::vector<Retainer<Item>> const& children() const {
        return _children;
    }

    void clear_children();

    bool set_children(std::vector<Item*> const& children, std::string* err_msg = nullptr);
    
    bool insert_child(int index, Item* child, std::string* err_msg = nullptr);

    bool set_child(int index, Item* child, std::string* err_msg = nullptr);

    bool remove_child(int index, std::string* err_msg = nullptr);

    bool append_child(Item* child, std::string* err_msg = nullptr) {
        return insert_child(_children.size(), child, err_msg);
    }

protected:
    virtual ~Composition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::vector<Retainer<Item>> _children;
    static std::string _composition_kind;
};

#endif
