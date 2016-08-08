import random
from datetime import datetime

import pandas as pd
import pytest

from matchwell import util, tree


TEST_LABELS = [
    'A',
    'A/B',
    'A/C',
    'A/D',
    'A/B/E',
    'A/B/F',
    'A/D/G',
    'A/D/H',
    'A/D/I'
]


def test_new_data_frame():
    df = util.new_data_frame()
    cols = [
        'timestamp',
        'type',
        'id',
        'raw',
        'text',
        'labels',
    ]
    for c in cols:
        assert c in df.columns


@pytest.yield_fixture()
def df():
    yield util.new_data_frame()


def test_newest(df):
    ts1 = pd.Timestamp(datetime(2016, 8, 8))
    ts2 = pd.Timestamp(datetime(2006, 8, 8))
    df.loc[ts1] = None
    df.loc[ts2] = None
    assert util.newest(df) == ts1
    assert util.newest(df, format=True) == "2016/08/08"


def test_collapse_unique():
    # Build a list of randomly sampled subsets of the master list
    l = [random.sample(TEST_LABELS, random.randint(0, len(TEST_LABELS)-1))
         for i in range(10)]
    assert sorted(list(util.collapse_unique(l))) == sorted(TEST_LABELS)


def test_build_prefix_tree():
    exp = {
        'A': {
            'A/B': {
                'A/B/E': {},
                'A/B/F': {}
            },
            'A/C': {},
            'A/D': {
                'A/D/G': {},
                'A/D/H': {},
                'A/D/I': {},
            }
        }
    }
    assert tree.build_prefix_tree(TEST_LABELS) == exp
