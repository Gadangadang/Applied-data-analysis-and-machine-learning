import numpy as np
import os
import sys


class NeuralNetwork:
    def __init__(self,
                 X,
                 y,
                 num_hidden_layers=1,
                 num_hidden_nodes=50,
                 epochs=10,
                 batch_size=100,
                 eta=0.1,
                 lmbd=0.0,
                 seed=4155):

        self.X = X  # Design matrix
        self.y = y  # Target
        self.num_hidden_layers = num_hidden_layers
        self.num_hidden_nodes = num_hidden_nodes
        self.epochs = epochs
        self.batch_size = batch_size
        self.eta = eta
        self.lmbd = lmbd
        self.seed = seed

    def create_biases_and_weights(self):
        np.random.seed(self.seed)
        self.hidden_weights = np.random.randn(
            self.X.shape[1], self.num_hidden_nodes)
        self.hidden_bias = np.zeros(self.num_hidden_nodes) + 0.01

    def feed_forward(self):
        pass

    def backpropagation(self):
        pass

    def sigmoid_activation(self, value):
        return 1 / (1 + np.exp(-value))

    def RELU_activation(self, value):
        if value > 0:
            return value
        else:
            return value

    def Leaky_RELU_activation(self, value):
        if value > 0:
            return value
        else:
            return 0.01 * value


if __name__ == "__main__":
    # Get modules from project 1
    path = os.getcwd()  # Current working directory
    path += '/../../Project 1/code'
    sys.path.append(path)
    from Functions import *

    #--- Create data from Franke Function ---#
    N = 5               # Number of points in each dimension
    z_noise = 0.2       # Added noise to the z-value
    n = 2               # Highest order of polynomial for X

    x, y, z = generate_data(N, z_noise)
    X = create_X(x, y, n)

    NN = NeuralNetwork(X, z)


#
