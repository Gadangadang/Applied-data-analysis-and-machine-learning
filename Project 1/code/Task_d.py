import numpy as np
from random import random, seed
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
from Functions import *
from matplotlib.ticker import MaxNLocator
from sklearn.utils import resample
from plot_set import * # Specifies plotting settings




def bootstrap(X_train, X_test, z_train, z_test, B, lamda):
    """
    info
    """

    z_pred = np.zeros((len(z_test), B))
    z_tilde = np.zeros((len(z_train), B))

    for i in range(B):
        X_res, z_res = resample(X_train, z_train)
        beta_OLS = RIDGE_regression(X_res, z_res, lamda)
        z_pred[:,i] = (X_test @ beta_OLS).ravel()
        z_tilde[:,i] = (X_train @ beta_OLS).ravel()

    return z_pred, z_tilde


def bias_variance_tradeoff_lamda(lamda_values, N, z_noise, n, B, plot = True):
    """
    write info
    """
    x, y, z = generate_data(N, z_noise, seed=2018)
    bias = np.zeros(n+1)
    variance = np.zeros(n+1)
    error = np.zeros(n+1)


    for lamda in lamda_values:
        for i in range(0,n+1): #For increasing complexity

            X = create_X(x, y, i)

            X_train, X_test, z_train, z_test = train_test_split(X, z, test_size=0.2)
            # print(np.shape(X_train), np.shape(X_test), np.shape(z_train), np.shape(z_test))

            X_train, X_test = scale_design_matrix(X_train, X_test)

            z_pred = bootstrap(X_train, X_test, z_train, z_test, B, lamda)
            bias[i] = np.mean((z_test - np.mean(z_pred, axis = 1, keepdims = True))**2) # axis = 1 => columns
            variance[i] = np.mean(np.var(z_pred, axis = 1))
            error[i] = np.mean(np.mean( (z_test-z_pred)**2, axis = 1, keepdims = True  ))

        n_arr = np.linspace(0,n,n+1)
        if plot:
            plt.figure(num=0, dpi=80, facecolor='w', edgecolor='k')
            plt.plot(n_arr, bias, label = "Bias")
            plt.plot(n_arr, variance, label = "Variance")
            plt.plot(n_arr, error, "--", label = "Error")
            plt.title(r"$\lambda$ = {:.3f}".format(lamda))
            ax = plt.gca()
            ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # Force integer ticks on x-axis
            plt.xlabel(r"$n$", fontsize=14)
            # plt.ylabel(r"MSE", fontsize=14)
            plt.legend(fontsize = 13)
            plt.tight_layout(pad=1.1, w_pad=0.7, h_pad=0.2)
            # plt.savefig(f"../article/figures/bias_variance_tradeoff.pdf", bbox_inches="tight")
            plt.show()


def Error_Complexity(lamda, N, z_noise, n, plot = True, seed = 4155):
    error_test, error_train = np.zeros(n+1), np.zeros(n+1)
    x, y, z = generate_data(N, z_noise, seed)
    z = standard_scale(z)

    for i in range(0,n+1):
        X = create_X(x, y, i)
        X_train, X_test, z_train, z_test = train_test_split(X, z, test_size=0.2)

        X_train, X_test = scale_design_matrix(X_train, X_test) #Scales X_train and X_test

        z_pred, z_tilde = bootstrap(X_train, X_test, z_train, z_test, B, lamda)
        error_test[i] = np.mean(np.mean( (z_test-z_pred)**2, axis = 1, keepdims = True  ))
        error_train[i] = np.mean(np.mean( (z_train-z_tilde)**2, axis = 1, keepdims = True  ))

    return error_test, error_train


def MSE_Ridge_bootstrap(N, z_noise, n, lamda_values):
    plt.figure(num=0, dpi=80, facecolor='w', edgecolor='k')

    for index, lamda in enumerate(lamda_values):

        plt.subplot(2,2,index+1)
        error_test, error_train = Error_Complexity(lamda, N, z_noise, n, plot = True, seed = 4155)
        n_arr = np.linspace(0,n,n+1)

        #---Plotting---#

        plt.title(r"Bootstrap MSE with $\lambda$ = {:.3f} ".format(lamda))
        plt.plot(n_arr, error_test, label = "Test")
        plt.plot(n_arr, error_train, label = "Train")
        plt.legend(fontsize = 13)



    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # Force integer ticks on x-axis
    plt.xlabel(r"$n$", fontsize=14)
    plt.ylabel(r"MSE", fontsize=14)

    plt.tight_layout(pad=1.1, w_pad=0.7, h_pad=0.2)
    # plt.savefig(f"../article/figures/Complexity_MSE{numRuns}.pdf", bbox_inches="tight")
    plt.show()




if __name__ == "__main__":
    #--- settings ---#
    N = 25            # Number of points in each dimension
    z_noise = 0.2     # Added noise to the z-value
    n = 14                 # Highest order of polynomial for X
    B = 100           # Number of iterations in boostrap

    ### Bootstrap analysis with Ridge
    lamda_values = np.logspace(-3,2,4)
    
    MSE_Ridge_bootstrap(N, z_noise, n, lamda_values)

    ### Cross-validation with Ridge

    ### Bias-variance tradeoff with Ridge

    #bias_variance_tradeoff_lamda(lamda_values, N, z_noise, n, B, plot = True)