"""
Neural Networks with No Imports (in Python).
"""

MERSENNE_PRIME = 162259276829213363391578010288127
A = 2305843009213693951
B = 15485863

def random(seed):
    """Pseudo-random number generator in the range [0, 1).

    “Mersenne prime twister”."""

    state = seed
    for _ in range(20):
        state = (state*A + B) % MERSENNE_PRIME
    while True:
        state = (state*A + B) % MERSENNE_PRIME
        cand = state/(MERSENNE_PRIME + 1)
        # Ignore the first 3 decimal places.
        yield 1000*cand - int(1000*cand)

def ensure_other_is_scalar(matrix_method):
    """Simple decorator to check if second argument to a matrix method is a scalar."""
    def wrapper(self, other, *args, **kwargs):
        if not isinstance(other, (int, float, complex)):
            raise ValueError(f"Cannot use {matrix_method} with 'other' of type {type(other)}.") 
        return matrix_method(self, other, *args, **kwargs)
    return wrapper

class Matrix:
    """Represents a matrix with numerical components."""

    rand_generator = random(id(73))

    def __init__(self, data, nrows=None, ncols=None):
        """(nrows, ncols) gives the shape of the matrix and
        data populates the matrix."""

        self.nrows = nrows if nrows is not None else len(data)
        self.ncols = ncols if ncols is not None else len(data[0])

        if isinstance(data, (int, float, complex)):
            data = [[data for _ in range(self.ncols)] for _ in range(self.nrows)]
        self.data = data

    def size(self):
        return self.nrows*self.ncols

    def t(self):
        return Matrix(
            [[self.data[r][c] for r in range(self.nrows)] for c in range(self.ncols)]
        )

    def __add__(self, other):
        """Add two matrices or a matrix and a scalar."""

        if isinstance(other, (int, float, complex)):
            return self.map(lambda elem: elem + other)
        elif isinstance(other, Matrix):
            return Matrix.interleave(lambda l, r: l + r, self, other)
        else:
            raise ValueError(f"Cannot add a matrix with {type(other)}.")

    def __sub__(self, other):
        """Subtract a matrix or a scalar from a matrix."""
        return self + (-1*other)

    def __mul__(self, other):
        """Multiply a matrix with a scalar."""

        if isinstance(other, (int, float, complex)):
            return self.map(lambda elem: elem * other)
        elif isinstance(other, Matrix):
            return Matrix.interleave(lambda l, r: l * r, self, other)
        else:
            raise ValueError(f"Cannot multiply a matrix with {type(other)}.")

    @ensure_other_is_scalar
    def __rmul__(self, other):
        return self*other

    @ensure_other_is_scalar
    def __truediv__(self, other):
        return self*(1/other)

    @ensure_other_is_scalar
    def __pow__(self, other, modulo=None):
        if modulo is None:
            return self.map(lambda elem: pow(elem, other))
        else:
            return self.map(lambda elem: pow(elem, other, modulo))

    @ensure_other_is_scalar
    def __lt__(self, other):
        return self.map(lambda elem: int(elem < other))

    @ensure_other_is_scalar
    def __le__(self, other):
        return self.map(lambda elem: int(elem <= other))

    @ensure_other_is_scalar
    def __eq__(self, other):
        return self.map(lambda elem: int(elem == other))

    @ensure_other_is_scalar
    def __ne__(self, other):
        return self.map(lambda elem: int(elem != other))

    @ensure_other_is_scalar
    def __gt__(self, other):
        return self.map(lambda elem: int(elem > other))

    @ensure_other_is_scalar
    def __ge__(self, other):
        return self.map(lambda elem: int(elem >= other))

    def map(self, f):
        """Map a function over all components of the matrix."""
        return Matrix([[f(elem) for elem in row] for row in self.data])

    @staticmethod
    def interleave(f, m1, m2):
        """Apply f on the corresponding pairs of elements of the two matrices."""
        data = []
        for row1, row2 in zip(m1.data, m2.data):
            data.append([f(e1, e2) for e1, e2 in zip(row1, row2)])
        return Matrix(data)

    @staticmethod
    def maximum(m1, m2):
        """Returns the component-wise maximum between two matrices."""

        if isinstance(m2, (int, float, complex)):
            return m1.map(lambda elem: max(elem, m2))
        elif isinstance(m2, Matrix):
            return Matrix.interleave(max, m1, m2)
        else:
            raise ValueError(f"Cannot find matrix maximum with argument of type {type(m2)}.")

    def argmax(self):
        """Returns the index of the largest value in the matrix."""
        idx = (0, 0)
        m = self.data[0][0]
        for r, row in enumerate(self.data):
            for c, elem in enumerate(row):
                if elem > m:
                    m = elem
                    idx = (r, c)
        return idx

    @staticmethod
    def dot(m1, m2):
        """Perform matrix multiplication."""

        # Check if the shapes of the matrices are compatible.
        if m1.ncols != m2.nrows:
            raise ValueError(
                f"Cols of left matrix ({m1.ncols}) != rows of right matrix ({m2.nrows})."
            )
        # Compute the data of the resulting matrix.
        data = []
        for r in range(m1.nrows):
            row = []
            for c in range(m2.ncols):
                row.append(
                    sum(m1.data[r][i]*m2.data[i][c] for i in range(m1.ncols))
                )
            data.append(row)
        return Matrix(data)

    @staticmethod
    def mean(m):
        return sum(sum(row) for row in m.data)/(m.size())

    @staticmethod
    def random(nrows, ncols):
        """Generate a (nrows by ncols) random matrix.

        The values are drawn from the uniform distribution in [-1, 1].
        """

        return Matrix(
            [[2*next(Matrix.rand_generator) - 1 for _ in range(ncols)]
            for _ in range(nrows)]
        )

class ActivationFunction:
    """'Abstract base class' for activation functions."""
    def f(self, x):
        raise NotImplementedError("Activation functions should define the f method.")

    def df(self, x):
        raise NotImplementedError("Activation functions should define the df method.")

class LeakyReLU(ActivationFunction):
    def __init__(self, alpha=0.1):
        self.alpha = alpha

    def f(self, x):
        return Matrix.maximum(x, self.alpha*x)

    def df(self, x):
        # return Matrix.maximum()
        return Matrix.maximum(x > 0, self.alpha)

class LossFunction:
    """'Abstract base class' for loss functions."""
    def loss(self, output, target):
        raise NotImplementedError("Loss functions should implement a loss method.")

    def dloss(self, output, target):
        """Derivative of the loss w.r.t. to the output variable."""
        raise NotImplementedError("Loss functions should implement a dloss method.")

class MSELoss(LossFunction):
    """Mean Squared Error loss function."""
    def loss(self, output, target):
        return Matrix.mean((output - target)**2)

    def dloss(self, output, target):
        return 2*(output - target)/(output.size())

class Layer:
    """An abstraction over a set of weights and biases between two sets of neurons."""
    def __init__(self, ins, outs, act_function):
        self.ins = ins
        self.outs = outs
        self.act_function = act_function
        self.W = Matrix.random(outs, ins)/(outs * ins)
        self.b = Matrix.random(outs, 1)/outs

    def forward_pass(self, x):
        """Propagate information forward."""
        return self.act_function.f(Matrix.dot(self.W, x) + self.b)

class NeuralNetwork:
    """An ordered collection of compatible layers."""
    def __init__(self, layers, loss, lr):
        self.layers = layers
        self.loss_function = loss
        self.lr = lr

        # Check that the layers are compatible.
        for l1, l2 in zip(layers[:-1], layers[1:]):
            if l1.outs != l2.ins:
                raise ValueError(f"Layers are not compatible ({l1.outs} != {l2.ins}).")

    def forward_pass(self, x):
        """Propagate a vector through the whole network."""

        out = x
        for layer in self.layers:
            out = layer.forward_pass(out)
        return out

    def loss(self, out, t):
        """Compute the loss of the network output."""
        return self.loss_function.loss(out, t)

    def train(self, x, t):
        """Train the network so that net.forward_pass(x) becomes closer to t."""

        xs = [x]
        for layer in self.layers:
            xs.append(layer.forward_pass(xs[-1]))

        dx = self.loss_function.dloss(xs.pop(), t)
        for layer, x in zip(self.layers[::-1], xs[::-1]):
            y = Matrix.dot(layer.W, x) + layer.b
            db = layer.act_function.df(y) * dx
            dW = Matrix.dot(db, x.t())

            layer.W = layer.W - self.lr * dW
            layer.b = layer.b - self.lr * db

            dx = Matrix.dot(layer.W.t(), db)


""" # Basic demo that shows empirically that the networks are working.
if __name__ == "__main__":
    l1 = Layer(2, 3, LeakyReLU())
    l2 = Layer(3, 4, LeakyReLU())
    l3 = Layer(4, 1, LeakyReLU())
    net = NeuralNetwork([l1, l2, l3], MSELoss(), 0.01)

    t = Matrix(0, 1, 1)
    inps = [Matrix.random(2, 1) for _ in range(100)]
    loss = 0
    for inp in inps:
        out = net.forward_pass(inp)
        loss += net.loss(out, t)
    print(f"Pre-training loss is {loss}")

    for _ in range(1000):
        net.train(Matrix.random(2, 1), t)

    loss = 0
    for inp in inps:
        out = net.forward_pass(inp)
        loss += net.loss(out, t)
    print(f"Post-training loss is {loss}")
"""

if __name__ == "__main__":
    layers = [
        Layer(784, 16, LeakyReLU()),
        Layer(16, 16, LeakyReLU()),
        Layer(16, 10, LeakyReLU()),
    ]
    net = NeuralNetwork(layers, MSELoss(), 0.001)

    def load_data(path):
        """Load MNIST data from a CSV file."""

        print(f"Now loading {path}...", end="")
        with open(path, "r") as f:
            lines = f.read().split("\n")[:-1]
        # Convert each number to an integer.
        data = [list(map(int, line.split(","))) for line in lines]
        print(" Done loading.")
        # Reformat the data into the (digit, pixels) format.
        return [(l[0], Matrix([l[1:]]).t()) for l in data]

    def test(net, test_data):
        # test_data is a list with (digit, pixels) pairs.
        correct = 0
        for i, (digit, pixels) in enumerate(test_data):
            if not i%1000:
                print(i)
            out = net.forward_pass(pixels)
            guess = out.argmax()[0]
            if guess == digit:
                correct += 1

        return correct/len(test_data)

    def train(net, train_data):
        ts = {}
        for digit in range(10):
            t = Matrix(0, 10, 1)
            t.data[digit][0] = 1
            ts[digit] = t

        for i, (digit, pixels) in enumerate(train_data):
            if not i % 1000:
                print(i)
            net.train(pixels, ts[digit])

    test_data = load_data("mnistdata/mnist_test.csv")
    print("Testing...")
    print(test(net, test_data))

    train_data = load_data("mnistdata/mnist_train.csv")
    print("Training... ", end="")
    train(net, train_data)
    print("Done training.")

    print("Testing...")
    print(test(net, test_data))
