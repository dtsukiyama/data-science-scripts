import matplotlib.pyplot as plt
import xgboost as xgb
import time
import numpy as np

from xgboost import plot_importance
from sklearn.cross_validation import train_test_split
from sklearn import metrics
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from collections import Counter
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


params = {
        'min_child_weight': [1, 5, 10],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'max_depth': [4, 5, 6],
        'scale_pos_weight':[0.9, 0.95, 0.99]
        }

def auc(true, predictions):
    fpr, tpr, thresholds = metrics.roc_curve(true, predictions)
    return metrics.auc(fpr, tpr)


def rocCurve(y_test, predictions):
    """
    Roc Curve construction derived from the following link:
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html
    """
    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    fpr, tpr, _ = metrics.roc_curve(y_test, predictions)
    roc_auc = metrics.auc(fpr, tpr)

    # Compute micro-average ROC curve and ROC area
    plt.title('Receiver Operating Characteristic')
    plt.plot(fpr, tpr, color='darkorange', label = 'AUC = %0.2f' % roc_auc)
    plt.legend(loc = 'lower right')
    plt.plot([0, 1], [0, 1], color='navy',linestyle='--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')


def boostClf(train, test, validation, train_label, valid_label, test_label, parameters,
                   epochs=500, early_stopping=20):
    
    d_train = xgb.DMatrix(train, label=train_label)
    d_test = xgb.DMatrix(test)
    d_valid = xgb.DMatrix(validation, label=valid_label)
    watchlist = [(d_train, 'train'), (d_valid, 'valid')]
    model = xgb.train(parameters, d_train, epochs, watchlist, early_stopping_rounds=early_stopping, verbose_eval=10)
    return model


def parameterSearch(num_folds, features, target):
    clf = xgb.XGBClassifier(learning_rate=0.1, n_estimators=100, objective='binary:logistic',
                        silent=True, nthread=1)
    param_comb = 5
    model_cv = StratifiedKFold(n_splits=num_folds, shuffle = True, random_state = 1001)
    random_search = RandomizedSearchCV(clf, 
                                       param_distributions=params, 
                                       n_iter=param_comb, 
                                       scoring='roc_auc',
                                       n_jobs=-1, 
                                       cv=model_cv.split(features, target), 
                                       verbose=3, 
                                       random_state=1001)
    print("Starting search...")
    start = time.time()
    random_search.fit(features, target)
    end = time.time()
    print("Search Finished")
    print("Search took {} seconds").format(end - start)
    return random_search


def auc_cv(model, n_folds, features, target):
    kf = KFold(n_folds, shuffle=True, random_state=12).get_n_splits(features.values)
    auc = cross_val_score(model, features.values, target, scoring="roc_auc", cv = kf)
    return(auc)


def probabilityOp(prediction_data):
    count = None
    probs = []
    for decile in [np.round(x * 0.1, 1) for x in range(1, 10)]:
        count = Counter(prediction_data.query('prob > @decile')['test'])
        if len(count) == 2:
            probs.append(count[1]*1.0/(count[0]+count[1]))
        else:
            probs.append(1)
            
    del count
    return list(zip([np.round(x * 0.1, 1) for x in range(1, 10)], probs))
