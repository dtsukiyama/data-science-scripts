"""
Working through an example
Let's walk through calculating the weights steps for a simple three layer network. 
Suppose there's two input units, one hidden unit, and one output unit, 
with sigmoid activations on the hidden and output units.
"""

import numpy as np

# activation function
def sigmoid(x):
    return 1/(1+(np.exp(-x)))

x = np.array([0.1, 0.3])
target = 1
learnrate = 0.5
weights_input_hidden = np.array([0.4, -0.2])
weights_hidden_output = np.array([0.1])

# calculate input to the hidden unit
hidden_layer_input = np.dot(x, weights_input_hidden)

#calculate the output of the hidden unit
hidden_layer_output = sigmoid(hidden_layer_input)

# calculate the output of the network
# sigmoid(0.1×0.495)=0.512.

output = sigmoid(weights_hidden_output*hidden_layer_output)

# calculate the error of the output unit
# (1−0.512)×0.512×(1−0.512)=0.122.

error = (target - output) * output * (target - output)

# calculate the error for the hidden unit with backpropagation
# 0.1×0.122×0.495×(1−0.495)=0.003

hidden_unit_error = weights_hidden_output * error * hidden_layer_output * (target - hidden_layer_output)

# calculate the gradient 
# 0.5×0.122×0.495=0.032

W = learnrate * error * hidden_layer_output

# calculate input to hidden weights

learnrate * hidden_unit_error * x[:, None]
