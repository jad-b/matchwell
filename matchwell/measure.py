import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics, cross_validation


def report(pred, y):
    accuracy = np.mean(pred == y) * 100.
    print("{:.2f}% accuracy on the training set".format(accuracy))
    print("Classification Report\n", metrics.classification_report(y, pred))
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