import re
import itertools
from collections import Iterable

import pandas as pd


def new_data_frame():
    """Returns a pre-initialized :class:`pandas.DataFrame` with the correct
    columns in place."""
    return pd.DataFrame(
        columns=[
            'timestamp',
            'type',
            'id',
            'raw',
            'text',
            'labels',
        ]
    )


def newest(df, format=False):
    """Return the newest timestamp from a :class:`pandas.DataFrame`."""
    ts = df.sort_index(ascending=False).index[0]
    if format:
        return ts.strftime("%Y/%m/%d")
    return ts


# String utiltities
def contains_substrings(substrs, coll, inverse=False):
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
    b = set(substrs).issubset(set(coll))
    if inverse:
        return not b
    return b


def intersection(a, b):
    """Return the intersection between `str` in A and B.

    Args:
        a (List[str]): List of strings.
        b (List[str]): List of strings.
    Returns:
        Set[str]
    """
    return set(a).intersection(set(b))


def iterable_or_string(val):
    """Returns if the value is A) Iterable, and B) a string."""
    is_iter, is_string = False, False
    if isinstance(val, Iterable):
        is_iter = True
        if isinstance(val, str):
            is_string = True
    return is_iter, is_string


def filter_children(labels, parent):
    """Filters for immediate descendents of a parent within a label list.

    Args:
        labels (List[str]): List of labels, with their ancestry denoted by
            slashes within.
        parent (str): Parent label to filter direct descendents on.

    Returns:
        List[str] of child labels.
    """
    pat = parent
    if pat != '':  # Root node check
        pat += '/'
    p = re.compile(pat + r'\w+$')
    for l in labels:
        m = p.match(l)
        if m is not None:
            yield l


def collapse_unique(iter_of_iters):
    """Collapse a iterable of iterables into a set of unique values."""
    unique_labels = set()
    for l in itertools.chain.from_iterable(iter_of_iters):
        unique_labels.add(l)
    return unique_labels
