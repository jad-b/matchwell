"""
tree.py
=======
Provides utilities for working with a tree of string labels.
"""
import networkx as nx


# General-purpose tree tools
def build_prefix_tree(words, delim='/'):
    """Create a prefix tree using nested dictionaries."""
    trie = {}
    for w in words:
        # print("Splitting", w)
        parts = w.split(delim)
        d = trie  # Essentially a pointer within our tree.
        for i in range(len(parts)):
            # print("\tPlacing", p)
            p = '/'.join(parts[:i+1])
            d.setdefault(p, {})
            d = d[p]
        d = trie  # Reset to top-level dict
        # print(d)
    return trie


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


def ancestral_walk(struct):
    """Walk a structure yielding (parent, current) tuples."""
    stack = []
    stack.append('')  # Root.
    for l, i in walk(struct):
        while len(stack) > i + 1:
            stack.pop()  # Reset our stack's context
        stack.append(l)
        yield (stack[i], stack[i+1])


# NetworkX
def from_labels(labels):
    """Create a :class:`networkx.DiGraph` from a list of labels."""
    # Isolate unique labels
    label_tree = build_prefix_tree(labels)
    edges = ancestral_walk(label_tree)
    # Build a tree from labels
    T = nx.DiGraph()
    T.add_edges_from(edges)
    return T


def find_root(G):
    """Returns root node ID for the Graph."""
    if not nx.is_tree(G):
        return None
    return nx.topological_sort(G)[0]
