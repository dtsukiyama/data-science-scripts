"" data: mnist = input_data.read_data_sets("MNIST_data/", one_hot=True) """


class softmax(object):
    
    def __init__(self, vector_space = 784, learning_rate = 0.5, training_step = 1000):
        self.vector_space = vector_space
        self.learning_rate = learning_rate
        self.training_step = training_step

    def fit(self, data):
        """ 
        train_data = mnist.train
        test_images = mnist.test.images
        test_labels = mnist.test.labels
        x is a placeholder, input when TensorFlow runs a computation
        For MNIST images, each is flattened into a 784-dimensional vector; represented as a 2-D tensor of floating point numbers
        w is weights and b is bias; set as tensors full of zeros. These will be learned
        y implements model
        multiply x by W with expression tf.matmul(x, W)
        y_ cross-entropy, which is the cost function
        """
        x = tf.placeholder(tf.float32, [None, self.vector_space])
        W = tf.Variable(tf.zeros([self.vector_space, 10]))
        b = tf.Variable(tf.zeros([10]))
        y = tf.nn.softmax(tf.matmul(x, W) + b)
        y_ = tf.placeholder(tf.float32, [None, 10])
        cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
        train_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(cross_entropy)
        init = tf.initialize_all_variables()
        sess = tf.Session()
        sess.run(init)
        for i in range(self.training_step):
            batch_xs, batch_ys = data.train.next_batch(100)
            sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
        correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print (sess.run(accuracy, feed_dict={x: data.test.images, y_: data.test.labels}))
