import matplotlib.pyplot as plt
import numpy as np
from scipy.special import expit
from sklearn import metrics, cross_validation


def report(y, pred, labels=()):
    print("{:.2f}% accuracy on the training set"
          .format(metrics.accuracy_score(y, pred)))
    print("Classification Report\n",
          metrics.classification_report(y, pred, target_names=labels))
    print("Confusion Matrix\n", metrics.confusion_matrix(y, pred))


def cv_scores(clf, X, y, cv=5, plot=False):
    scores = cross_validation.cross_val_score(clf, X, y, cv)
    print("Scores:\n" + '\n'.join((str(x) for x in scores)))
    if plot:
        for i, name in enumerate(scores):
            plt.subplot(len(scores), 1, i + 1)
            plt.bar(np.arange(1, 6), scores[name], color="#348ABD")
            # Plot the mean as a horizontal line
            plt.axhline(y=scores[name].mean(), color='r', linestyle='-')
            plt.xlim(0, 7)
            plt.ylim(.0, 1.)
    return scores


def show_confidence(clf, X, plot=False):
    """Analyze prediction confidence."""
    confs = clf.decision_function(X)
    if plot:
        plt.hist(confs, bins=20)
    # Maybe a scatter plot w/ different coloring per label to show
    # mis-categorization, which hopefully is contained close to zero.
    print(np.array_str(expit(confs) * 100, precision=2))
