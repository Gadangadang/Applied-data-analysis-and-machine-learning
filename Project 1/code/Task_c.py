import numpy as np
import matplotlib.pyplot as plt
from random import random, seed
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso

from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
from Functions import *
from matplotlib.ticker import MaxNLocator



def compaire_CV_B(N, z_noise, n, B, k_fold_number, method, lamda = 0):
    x, y, z = generate_data(N, z_noise, seed=2018)

    error_CV = np.zeros(n + 1)
    error_B = np.zeros(n + 1)
    error_sklearn = np.zeros(n + 1)
    if method == "OLS":
        sklearMethod = LinearRegression(fit_intercept=False)
    elif method == "Ridge":
        sklearMethod = Ridge()
    elif method == "Lasso":
        sklearMethod = Lasso(lamda, tol = 0.0, fit_intercept = False)
    for i in range(0, n + 1):  # For increasing complexity
        X = create_X(x, y, i)

        X_train, X_test, z_train, z_test = train_test_split(
            X, z, test_size=0.2)

        #X_train, X_test = scale_design_matrix(X_train, X_test)

        z_pred_B = bootstrap(X_train, X_test, z_train, z_test, B, method, lamda)

        error_CV[i] = cross_validation(X, z, k_fold_number, method, lamda)
        error_B[i] = np.mean(
            np.mean((z_test - z_pred_B)**2, axis=1, keepdims=True))

    n_arr = np.linspace(0, n, n + 1)

    plt.figure(num=0, dpi=80, facecolor='w', edgecolor='k')
    plt.plot(n_arr, error_CV, label="Cross validation ")
    plt.plot(n_arr, error_B, label="Bootstrap")

    ax = plt.gca()
    # Force integer ticks on x-axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xlabel(r"$n [complexity]$", fontsize=14)
    plt.ylabel(r"MSE", fontsize=14)
    plt.title(r"Bootstrap iterations: {}, K-folds: {}".format(B,
                                                              k_fold_number), fontsize=16)
    plt.legend(fontsize=13)
    plt.tight_layout(pad=1.1, w_pad=0.7, h_pad=0.2)
    plt.show()


if __name__ == "__main__":
    N = 30
    z_noise = 0.1
    n = 10
    B = 100
    k_fold_number = 10
    method = "OLS"
    compaire_CV_B(N, z_noise, n, B, k_fold_number, method)
