"""
================================
ROC Curve with Visualization API
================================
Scikit-learn defines a simple API for creating visualizations for machine
learning. The key features of this API is to allow for quick plotting and
visual adjustments without recalculation. In this example, we will demonstrate
how to use the visualization API by comparing ROC curves.
"""
print(__doc__)

##############################################################################
# Load Data and Train a SVC
# -------------------------
# First, we load the wine dataset and convert it to a binary classification
# problem. Then, we train a support vector classifier on a training dataset.
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import plot_roc_curve
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.neural_network import MLPClassifier


from app.dame_gender import Gender
from app.dame_sexmachine import DameSexmachine
from app.dame_utils import DameUtils

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('ml', choices=['nltk', 'svc', 'sgd', 'gaussianNB', 'multinomialNB', 'bernoulliNB', 'forest', 'tree', 'mlp'])
parser.add_argument('--verbose', default=False, action="store_true")
args = parser.parse_args()


ds = DameSexmachine()
X = np.array(ds.features_list(path="files/names/allnoundefined.csv"))
y = ds.gender_list(path="files/names/allnoundefined.csv")
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

if (args.verbose):
    print(X)
    print(y)

if (args.ml == "svc"):
    svc = SVC(random_state=42)
    svc.fit(X_train, y_train)
    svc_disp = plot_roc_curve(svc, X_test, y_test)


elif (args.ml == "forest"):
    rfc = RandomForestClassifier(n_estimators=10, random_state=42)
    rfc.fit(X_train, y_train)
    ax = plt.gca()
    rfc_disp = plot_roc_curve(rfc, X_test, y_test, ax=ax, alpha=0.8)
    rfc_disp.plot(ax=ax, alpha=0.8)

    
elif (args.ml == "sgd"):
    clf = SGDClassifier(loss="log").fit(X_train, y_train)
    sgd_disp = plot_roc_curve(clf, X_test, y_test)

elif (args.ml == "gaussianNB"):
    # Create a Gaussian Classifier
    model = GaussianNB()
    # Train the model using the training sets
    model.fit(X_train, y_train)
    disp = plot_roc_curve(model, X_test, y_test)
    
elif (args.ml == "multinomialNB"):
    # Create a Multinomial Classifier
    model = MultinomialNB()
    # Train the model using the training sets
    model.fit(X_train, y_train)
    disp = plot_roc_curve(model, X_test, y_test)
    
elif (args.ml == "bernoulliNB"):
    # Create a Bernoulli Classifier
    model = BernoulliNB()
    # Train the model using the training sets
    model.fit(X_train, y_train)
    disp = plot_roc_curve(model, X_test, y_test)

elif (args.ml == "tree"):
    # Create a tree Classifier
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X_train, y_train)
    disp = plot_roc_curve(clf, X_test, y_test)
    
    
plt.show()

    
##############################################################################
# Plotting the ROC Curve
# ----------------------
# Next, we plot the ROC curve with a single call to
# :func:`sklearn.metrics.plot_roc_curve`. The returned `svc_disp` object allows
# us to continue using the already computed ROC curve for the SVC in future
# plots.

# svc_disp = plot_roc_curve(svc, X_test, y_test)
# plt.show()


# ##############################################################################
# # Training a Random Forest and Plotting the ROC Curve
# # --------------------------------------------------------
# # We train a random forest classifier and create a plot comparing it to the SVC
# # ROC curve. Notice how `svc_disp` uses
# # :func:`~sklearn.metrics.RocCurveDisplay.plot` to plot the SVC ROC curve
# # without recomputing the values of the roc curve itself. Furthermore, we
# # pass `alpha=0.8` to the plot functions to adjust the alpha values of the
# # curves.
# rfc = RandomForestClassifier(n_estimators=10, random_state=42)
# rfc.fit(X_train, y_train)
# ax = plt.gca()
# rfc_disp = plot_roc_curve(rfc, X_test, y_test, ax=ax, alpha=0.8)
# svc_disp.plot(ax=ax, alpha=0.8)
# plt.show()