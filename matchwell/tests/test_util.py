import random

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
