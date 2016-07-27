import pickle

import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from matchwell import tree, util


class HierarchicalClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self):
        pass

    def fit(self, X, y, verbose=False):
        """Train the model.

        Setup
            1. Build Tree from labels in `y`
            2. Build & train models for each parent node
                a. Filter `y` to only contain child labels of parent
                b. Convert to a binary array of classes


        Training:
            for p in parents:
                y_scoped = get_classes_by_level(T, parent, y)
                p.fit(X, y_scoped)

        Args:
            X (pandas.Series): Raw text.
            y (List[str]): Associated labels for each training value.
        """
        # Build a set of unique values
        self._all_classes = tree.collapse_unique(y)
        if verbose:
            print("Classes: ", self._all_classes)
        # Create an ancestral tree of all labels
        self._tree = tree.from_labels(self._all_classes)
        if verbose:  # Save a PNG of the tree
            nx.draw(self._tree, pos=nx.spring_layout(self._tree))
            plt.tight_layout()
            plt.savefig("hc_tree.png", format="PNG")
        # For each level of the tree
        for n in self._tree.nodes:
            print('Training', n)
            # Create a model
            clf = SGDClassifier(
                loss='hinge', penalty='l2', alpha=1e-3, n_iter=5,
                random_state=42)
            # Filter target array to only contain child labels for this node.
            y_scoped = y.apply(
                lambda x: util.intersection(x, self._tree.successors(n)))
            self._tree[n]['classes'] = util.collapse_unique(y_scoped)
            # Convert to binary array
            y_binary = MultiLabelBinarizer().fit_transform(y_scoped)
            self._tree[n]['clf'] = clf.fit(X, y_binary)
            # RESUME

    def predict(self, X):
        """Create a predicted network of labels for the actual label.

        Returns:
            (dict[string]float32): Probability by node name.
        """
        return None

    def score(self, X, y):
        """Compare the quality of the label.

        The

        Args:
            X (pandas.Series): Raw text.
            y (List[str]): Associated labels for each training value.
        """
        return 1


def build_pipeline(clf, X, y):
    pl = Pipeline([
        ('vect', CountVectorizer(
            stop_words='english', strip_accents='unicode', analyzer='word')),
        ('tfidf', TfidfTransformer()),
        ('clf', clf)
    ])
    return pl.fit(X, y)


def grid_search(clf, params, X, y):
    gs_clf = GridSearchCV(clf, params, n_jobs=-1)
    gs_clf = gs_clf.fit(X, y)
    return gs_clf


def grid_search_optimal_parameters(gs_clf):
    best_params, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
    return best_params


def save_model(filename, clf):
    with open(filename, 'wb') as f:
        pickle.dump(clf, f)


def load_model(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
