import os
import sys
import autograd.numpy as np
from autograd import elementwise_grad
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from plot_set import *
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)


class NeuralNetwork:
    """
    Neural Network using stochastic gradient descent with optional
    momentum, for faster convergence. The basis of the algorithm is:

    *
    *
    *
    *
    """

    def __init__(self,
                 X,
                 t,
                 num_hidden_layers=1,
                 num_hidden_nodes=10,
                 batch_size=4,
                 eta=0.001,
                 lmbd=0.00,
                 gamma=0.0,
                 seed=4155,
                 activation="sigmoid",
                 cost="MSE",
                 loss = "MSE",
                 callback = False):
        """Initialization function for neural network.

        Args:
            X                 (Numpy ndarray): Matrix containing data to train on
            t                 (Numpy ndarray): Matrix/array containing target data
            num_hidden_layers (int, optional): Number of hidden layers.
                                               Defaults to 1.
            num_hidden_nodes  (int, optional): Number of hidden nodes per layer.
                                               Defaults to 10.
            batch_size        (int, optional): Size of data batch for SGD. Defaults to 4.
            eta             (float, optional): Learning rate for NN. Defaults to 0.001.
            lmbd            (float, optional): Regularization parameter. Defaults to 0.00.
            gamma           (float, optional): Momentum parameter. Defaults to 0.0.
            seed              (int, optional): Random seed, for SGD. Defaults to 4155.
            activation        (str, optional): Choice of activation function.
                                               Defaults to "sigmoid".
            cost              (str, optional): Choice of cost function. Defaults to "MSE".
            loss              (str, optional): Choice of loss func, for realtime tracking of accuracy.
                                               Defaults to "MSE".
            callback         (bool, optional): Bool, choice to track progress and loss accuracy.
                                               Defaults to False.
        """

        "---- Initialize object parameters ----"
        self.X = X  # Design matrix shape: N x features --> features x N
        self.t = t  # Target, shape: categories x N
        self.T = np.copy(t)

        self.N = X.shape[0]
        self.data_indices = np.arange(self.N)
        self.num_features = X.shape[1]
        self.num_categories = t.shape[1]

        self.num_hidden_layers = num_hidden_layers
        self.num_hidden_nodes = num_hidden_nodes
        self.num_output_nodes = self.num_categories
        self.L = self.num_hidden_layers + 2  # number of layer in total
        self.scaled_weight = [1,1,1]

        self.batch_size = batch_size
        self.lmbd = lmbd
        self.gamma = gamma
        self.seed = seed

        self.eta_0 = eta
        self.k = 0
        self.dropp_time = 0
        self.amplitude = 2

        self.tol = 1e-8


        "---- Set activation, cost, derivation and loss functions ----"
        if activation == "sigmoid":
            self.activation = self.sigmoid_activation
        elif activation == "relu":
            self.activation = self.RELU_activation
            self.scaled_weight = [num_hidden_nodes**2, \
            num_hidden_nodes*self.num_features, self.num_output_nodes * num_hidden_nodes ]
            print(self.scaled_weight)
        elif activation == "leaky_relu":
            self.activation = self.Leaky_RELU_activation
            self.scaled_weight = [num_hidden_nodes**2, \
            num_hidden_nodes*self.num_features, self.num_output_nodes * num_hidden_nodes]
        elif activation == "soft_max":
            self.activation = self.soft_max_activation
        if cost == "MSE":
            self.cost = self.MSE
        elif cost == "cross_entropy":
            self.cost = self.cross_entropy
            
        "---- Create hidden layers, weights and biases ----"
        self.create_layers()
        self.create_biases_and_weights()

        self.activation_der = elementwise_grad(self.activation)
        self.cost_der = elementwise_grad(self.cost)
        self.score_shape = 1

        if loss == "accuracy":
            self.score_func = self.accuracy_score
            self.score_shape = self.num_categories
        elif loss == "MSE":
            self.score_func = self.MSE_score
        elif loss == "R2":
            self.score_func = self.R2_score
        elif loss == "probability":
            self.score_func = self.probability_score

        self.callback_label = loss
        if callback:
            self.callback_print = lambda epoch, score_epoch: print(f"epoch: {epoch}, {self.callback_label} = {score_epoch}")
        else:
             self.callback_print = lambda epoch, score_epoch: None

    def create_layers(self):
        """
        layers_a: contain activation values of all nodes
        layers_z: contain weighted sum z / unactivated values of all nodes
        """
        self.layers_a = [np.zeros((self.N, self.num_hidden_nodes), dtype=np.float64)
                         for i in range(self.num_hidden_layers)]  # Intialized with the hidden layers

        self.layers_a.insert(0, self.X.copy())  # Add input layer
        self.layers_a.append(
            np.zeros((np.shape(self.t)), dtype=np.float64))  # Add output layer
        self.layers_z = self.layers_a.copy()

    def create_biases_and_weights(self):
        np.random.seed(self.seed)
        num_hidden_layers = self.num_hidden_layers
        num_features = self.num_features
        num_hidden_nodes = self.num_hidden_nodes
        num_categories = self.num_categories
        bias_shift = 0.1
        print(self.scaled_weight)
        self.weights = [np.random.randn(
            num_hidden_nodes, num_hidden_nodes)/(self.scaled_weight[0]) for i in range(num_hidden_layers - 1)]
        self.weights.insert(0, np.random.randn(num_hidden_nodes, num_features)/(self.scaled_weight[1]))

        # insert unused weight to get nice indexes
        self.weights.insert(0, np.nan)
        self.weights.append(np.random.randn(
            self.num_output_nodes, num_hidden_nodes)/(self.scaled_weight[2]))

        self.bias = [np.ones(num_hidden_nodes) * bias_shift
                     for i in range(num_hidden_layers)]
        self.bias.insert(0, np.nan)  # insert unused bias to get nice indexes
        self.bias.append(np.ones(num_categories) * bias_shift)

        # velocity for momentum
        self.vel_weights = [np.nan]
        self.vel_bias = [np.nan]
        for i in range(1, num_hidden_layers + 2):
            self.vel_weights.append(np.zeros(np.shape(self.weights[i])))
            self.vel_bias.append(np.zeros(np.shape(self.bias[i])))

        # local gradient
        self.local_gradient = self.layers_a.copy()  # also called error
        self.local_gradient[0] = np.nan  # don't use first

    def update_parameters(self):
        self.backpropagation()
        if self.check_grad > self.tol and np.isfinite(self.check_grad):
            for l in range(1, self.L):
                self.vel_weights[l] = self.gamma * self.vel_weights[l] + self.eta * (
                    self.local_gradient[l].T @ self.layers_a[l - 1] + self.weights[l] * self.lmbd)
                self.weights[l] -= self.vel_weights[l]

                self.vel_bias[l] = self.gamma * self.vel_bias[l] + \
                    self.eta * np.mean(self.local_gradient[l], axis=0)
                self.bias[l] -= self.vel_bias[l]

    def feed_forward(self):
        for l in range(1, self.L):
            Z_l = self.layers_a[l - 1] @ self.weights[l].T + \
                self.bias[l][np.newaxis, :]
            self.layers_z[l] = Z_l
            self.layers_a[l] = self.activation(Z_l)


    def backpropagation(self):
        self.local_gradient[-1] = self.cost_der(
            self.layers_a[-1]) * self.activation_der(self.layers_z[-1])

        for l in reversed(range(1, self.L - 1)):
            self.local_gradient[l] = self.local_gradient[l + 1]\
                @ self.weights[l + 1] * self.activation_der(self.layers_z[l])

        self.check_grad = np.linalg.norm(self.local_gradient[-1]*self.eta)

    def predict(self, X):
        self.layers_a[0] = X
        self.feed_forward()
        return self.sigmoid_activation(self.layers_z[-1])

    def train_network_stochastic(self, epochs, plot=False):
        self.score = np.zeros((epochs + 1, self.score_shape))
        self.check_grad = 1
        epoch = 0

        self.score[epoch] = self.get_score(self.X, self.T)
        self.callback_print(epoch, self.score[epoch])

        while epoch < epochs and self.check_grad > self.tol and np.isfinite(self.check_grad):
            self.eta_func(epoch)
            batches = self.get_batches()
            for batch in batches:
                self.choose_mini_batch(batch)
                self.feed_forward()
                self.update_parameters()
            self.score[epoch] = self.get_score(self.X, self.T)
            self.callback_print(epoch, self.score[epoch])
            epoch += 1
        self.num_epochs = epoch


    def plot_score_history(self, name=None, legend = []):
        plt.figure(num=0, dpi=80, facecolor='w', edgecolor='k')
        if self.num_epochs > 150:
            linestyle = "-"
            marker = "None"
        else:
            linestyle = "--"
            marker = "o"
        markersize = 3

        plt.plot(np.linspace(0, self.num_epochs, self.num_epochs),
                 self.score[:self.num_epochs], linestyle=linestyle, marker=marker, markersize=markersize)
        plt.xlabel("epoch", fontsize=14)
        plt.ylabel(self.callback_label, fontsize=14)
        if self.score.shape[1] > 1:
            if len(legend) == 0: # no legend in arg
                plt.legend(["category " + str(i)
                       for i in range(self.score.shape[1])], fontsize=13)
            else: # legend from arg
                plt.legend(legend)
        plt.tight_layout(pad=1.1, w_pad=0.7, h_pad=0.2)
        if isinstance(name, str):
            plt.savefig(f"../article/figures/{name}_score_history.pdf",
                    bbox_inches="tight")
        plt.show()


    def get_batches(self):
        idx = np.arange(self.N)
        np.random.shuffle(idx)
        int_max = self.N // self.batch_size
        batches = [
            idx[i * self.batch_size:(i + 1) * self.batch_size] for i in range(int_max)]
        if self.N % self.batch_size != 0:
            batches.append(idx[int_max * self.batch_size:])
        return batches

    def choose_mini_batch(self, batch):
        self.layers_a[0] = self.X[batch]
        self.t = self.T[batch]

    """
    Activation funtions
    """

    def sigmoid_activation(self, value):
        return 1.0 / (1.0 + np.exp(-value))

    def RELU_activation(self, value):
        vals = np.where(value > 0, value, 1e-8)
        return vals

    def Leaky_RELU_activation(self, value):
        vals = np.where(value > 0, value, 0.01 * value)
        return vals

    def soft_max_activation(self, value):
        val_exp = np.exp(value)
        return val_exp / (np.sum(val_exp, axis=1, keepdims=True))


    def get_score(self, X, target):
        self.layers_a[0] = X
        self.feed_forward()
        return self.score_func(X, target)

    """
    Score functions
    """

    def accuracy_score(self, X, target):
        pred = self.predict(X)
        hits = np.sum(np.around(pred) == target, axis=0)
        possible = target.shape[0]
        acc = hits / possible
        return acc

    def MSE_score(self, X, target):
        pred = self.predict(X)
        return np.mean((pred - target)**2)

    def R2_score(self, X, target):
        ymod = self.predict(X)
        target = target
        return 1 - np.sum((target - ymod)**2) /\
            np.sum((target - np.mean(target, axis=0) ** 2))

    def probability_score(self, X, target):
        pred = self.soft_max_activation(self.layers_z[-1])
        guess = np.argmax(pred, axis=1)
        target = np.argmax(target, axis=1)
        val = np.sum(guess == target) / len(target)
        return val

    """
    Cost funtions
    """

    def MSE(self, y_tilde):
        return (y_tilde - self.t)**2

    def cross_entropy(self, y_tilde):
        return -(self.t * np.log(y_tilde) + (1 - self.t) * np.log(1 - y_tilde))

    """
    Eta functions
    """

    def eta_func(self, epoch):
        self.eta = self.eta_0 * self.amplitude*self.sigmoid_activation(self.k*(self.dropp_time-epoch))

    def set_eta_decay(self, k, dropp_time):
        self.amplitude = 1
        self.k = k #steepness
        self.dropp_time = dropp_time #time of half decay


    def __str__(self):
        text = "Information of the Neural Network \n"
        text += "--------------------------------- \n"
        text += "Hidden layers:                 {} \n".format(self.num_hidden_layers)
        text += "Hidden nodes in network:       {} \n".format(self.num_hidden_nodes*\
                                                              self.num_hidden_layers)
        text += "Output nodes:                  {} \n".format(self.num_output_nodes)
        text += "Number of features:            {} \n".format(self.X.shape[1])
        text += "--------------------------------- \n"
        return text



if __name__ == "__main__":
    # Get modules from project 1
    path = os.getcwd()  # Current working directory
    path += '/../../Project 1/code'
    sys.path.append(path)
    from Functions import *
    # The above imports numpy as np so we have to redefine:
    import autograd.numpy as np
    #--- Create data from Franke Function ---#
    N = 5               # Number of points in each dimension
    z_noise = 0       # Added noise to the z-value
    n = 3               # Highest order of polynomial for X
    epochs = 50

    batch_size = int(N * N * 0.8)
    x, y, z = generate_data(N, z_noise)
    X = create_X(x, y, n)
    X_train, X_test, Z_train, Z_test = train_test_split(X, z, test_size=0.2)
    beta = OLS_regression(X_train, Z_train)
    z_ols = X_test @ beta
    NN = NeuralNetwork(X_train,
                       Z_train,
                       num_hidden_layers=4,
                       num_hidden_nodes=5,
                       batch_size=batch_size,
                       eta=0.001,
                       lmbd=0.0,
                       gamma=0,
                       seed=4155,
                       activation="sigmoid",
                       cost="MSE",
                       loss="R2",
                       callback=True)
    print(NN)
    NN.train_network_stochastic(epochs, plot=False)
    print(NN.get_score(X_test, Z_test))
