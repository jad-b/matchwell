from collections import Iterable


def contains_substring(substr, coll, inverse=False):
    """Return True if substr is contained within any element
    in the collection.

    Args:
        substr (str): Substring to search for.
        coll (Iterable[str]): Iterable of strings
        inverse (bool): Invert matching; return hits when substr
            is _not_ present.
    Returns:
        True if substring was found, else False.
    """
    if inverse:
        return any(True for x in coll if substr not in x)
    return any(True for x in coll if substr in x)


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


def ancestral_walk(struct):
    """Walk a structure yielding (parent, current) tuples."""
    stack = []
    stack.append('')  # Root.
    for l, i in walk(struct):
        while len(stack) > i + 1:
            stack.pop()  # Reset our stack's context
        stack.append(l)
        yield (stack[i], stack[i+1])


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
