import pytest
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB

from matchwell.measure import report, cv_scores
from matchwell.models import build_pipeline, grid_search


@pytest.yield_fixture(scope='session')
def X():
    yield pd.DataFrame()


@pytest.yield_fixture(scope='session')
def y():
    yield pd.Series()


def test_classifiers(X, y):
    clfs = (
        MultinomialNB(),
        SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3,
                      n_iter=5, random_state=42)
    )
    for clf in clfs:
        pl = build_pipeline(clf, X, y)
        pred = pl.predict(X)
        report(y, pred)
        cv_scores(pl, X, y)


def test_grid_search(X, y):
    parameters = {
        'vect__ngram_range': [(1, 1), (1, 2)],
        'vect__max_df': (.5, .75, 1.),
        'tfidf__use_idf': (True, False),
        'tfidf__norm': ('l1', 'l2'),
        'clf__alpha': (1e-2, 1e-3),
        'clf__penalty': ('l2', 'elasticnet'),
        'clf__n_iter': (10, 50, 80),
    }
    clf = build_pipeline(SGDClassifier())
    gs_clf = grid_search(clf, parameters, X, y)
    # Report on grid search outcome
    print("Best score: %0.3f" % gs_clf.best_score_)
    cv_scores(gs_clf, X, y, plot=True)
