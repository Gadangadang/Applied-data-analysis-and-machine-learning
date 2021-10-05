import numpy as np
from random import random, seed
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
from Functions import *
from matplotlib.ticker import MaxNLocator
from sklearn.utils import resample
from plot_set import *  # Specifies plotting settings
from Task_b2 import bias_variance_tradeoff
from Task_c import compaire_CV_B


def complexity_CV(data, n, k_fold_number, method, lamda = 0, plot=True, seed=4155):
    k = 0
    x,y,z = data
    for lmb in lamda:
        MSE_test, MSE_train = np.zeros(n + 1), np.zeros(n + 1)
        for i in range(0, n + 1):
            X = create_X(x, y, i)
            MSE_test[i], MSE_train[i] = cross_validation(X, z, k_fold_number, method, lmb, include_train= True)

        if plot:
            #---Plotting---#
            n_arr = np.linspace(0, n, n + 1)

            plt.figure(num=0, figsize=(8, 6),
                       facecolor='w', edgecolor='k')
            plt.subplot(2, 2, k + 1)
            if method == "OLS":
                plt.title(f"{method}: N = {N}", size=14)
            else:
                plt.title(
                    f"{method} $\lambda = ${lmb:.4f} : N = {N}", size=14)
            plt.plot(n_arr[1:], MSE_train[1:], label="Train")
            plt.plot(n_arr[1:], MSE_test[1:], label="Test")
            ax = plt.gca()
            # Force integer ticks on x-axis
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xlabel(r"$n$", fontsize=14)
            plt.ylabel(r"MSE", fontsize=14)

            # plt.ylabel(r"MSE", fontsize=14)
            plt.tight_layout()
            if k == 0:
                plt.legend(fontsize=13)


        k += 1
    plt.show()

if __name__ == "__main__":
    #--- settings ---#
    N = 15          # Number of points in each dimension
    z_noise = 0.2     # Added noise to the z-value
    n = 15                # Highest order of polynomial for X
    B = "N"            # Number of training points
    method = "Lasso"
    lamda = np.logspace(-5, -2, 4)
    k_fold_number = 5

    bias_variance_tradeoff(N, z_noise, n, "N", method, lamda, plot=True)

    #compaire_CV_B(N, z_noise, n, N * N, k_fold_number, method, lamda=1e-3)
    #complexity_CV(generate_data(N, z_noise, seed=4155), n, k_fold_number, method, lamda, plot=True, seed=4155)
