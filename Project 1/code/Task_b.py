import numpy as np
from random import random, seed
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
from Functions import *
from matplotlib.ticker import MaxNLocator

from plot_set import * # Specifies plotting settings

def Error_Complexity(N, z_noise, n, plot = True, seed = 4155):
    error_test, error_train = np.zeros(n+1), np.zeros(n+1)
    x, y, z = generate_data(N, z_noise, seed)
    z = standard_scale(z)
    for i in range(0,n+1):
        X = create_X(x, y, i)
        X_train, X_test, z_train, z_test = train_test_split(X, z, test_size=0.2)

        scaler = StandardScaler()
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)

        # Force first column of X back to 1
        X_train[:,0] = 1.
        X_test[:,0] = 1.

        beta_OLS = OLS_regression(X_train, z_train)

        ztilde = X_train @ beta_OLS
        zpredict = X_test @ beta_OLS

        error_test[i] = MSE(z_test,zpredict)
        error_train[i] = MSE(z_train,ztilde)


    if plot:
        import matplotlib.pyplot as plt
        n_arr = np.linspace(0,n,n+1)
        plt.plot(n_arr, error_test, label = "Test")
        plt.plot(n_arr, error_train, label = "Train")
        plt.legend()
        plt.show()

    return error_test, error_train


def multiple_avg(N, z_noise, n, numRuns):
    error = np.zeros((numRuns, 2, n+1)) # [i, (error_test, error_train), n]

    # Print process
    info_string = "Multirun avg, #run: "
    print(f"\r{info_string}0/{numRuns}", end = "")

    # Perform multiple runs
    for i in range(numRuns):
        error_test, error_train = Error_Complexity(N, z_noise, n, plot = False, seed = None)
        error[i,0] = error_test
        error[i,1] = error_train
        print(f"\r{info_string}{i+1}/{numRuns}", end = "")
    print(" (done)")

    #Find average
    avg = np.mean(error, axis = 0)
    n_arr = np.linspace(0,n,n+1)


    #---Plotting---#
    plt.figure(num=0, dpi=80, facecolor='w', edgecolor='k')
    plt.title(f"Avg. MSE for {numRuns} runs with {N} datapoints (noise =  {z_noise}" + r" $\times$ $N(0,1)$)")
    plt.plot(n_arr, avg[0], label = "Test")
    plt.plot(n_arr, avg[1], label = "Train")
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # Force integer ticks on x-axis
    plt.xlabel(r"$n$", fontsize=14)
    plt.ylabel(r"MSE", fontsize=14)
    plt.legend(fontsize = 13)
    plt.tight_layout(pad=1.1, w_pad=0.7, h_pad=0.2)
    plt.savefig(f"../article/figures/Complexity_MSE{numRuns}.pdf", bbox_inches="tight")
    plt.show()



if __name__ == "__main__":
    N = 50              # Number of points in each dimension
    z_noise = 0.8       # Added noise to the z-value
    n = 20              # Highest order of polynomial for X

    multiple_avg(N, z_noise, n, numRuns = 10)
