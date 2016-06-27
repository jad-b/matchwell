import pickle

from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV


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
