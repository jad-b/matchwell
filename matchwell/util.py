from collections import Iterable


def walk(val, level=0, leaves=True):
    """Walk a structure made of a dicts/lists."""
    if isinstance(val, dict):
        for k, v in sorted(val.items()):
            yield k, level
            yield from walk(v, level + 1, leaves=leaves)
    elif isinstance(val, list):
        for item in val:

            yield from walk(item, level + 1, leaves=leaves)
    elif leaves:
        yield val, level


def tree(struct, filtr=''):
    gen = walk(struct)
    for key, lvl in gen:
        if key in filtr:
            yield next(gen)


def build_prefix_tree(words, delim='/'):
    """Create a path tree using nested dictionaries.

    A "path" here is defined here as a series of words, separated by a
    delimiter. Each
    """
    trie = {}
    for w in words:
        # print("Splitting", w)
        parts = w.split(delim)
        d = trie  # Essentially a pointer within our tree.
        for p in parts:
            # print("\tPlacing", p)
            d.setdefault(p, {})
            d = d[p]
        d = trie  # Reset to top-level dict
        # print(d)
    return trie


def iterable_or_string(val):
    """Returns if the value is A) Iterable, and B) a string."""
    is_iter, is_string = False, False
    if isinstance(val, Iterable):
        is_iter = True
        if isinstance(val, str):
            is_string = True
    return is_iter, is_string
