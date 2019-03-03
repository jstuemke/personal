import numpy as np
from matplotlib import pyplot as plt
import scipy.integrate as intgr


def integrate(fcn, a, b):

    return intgr.quad(fcn, a, b)


def riemann_sum(fcn, a, b, num_rectangles=10):

    dx = (b - a) / num_rectangles
    return sum([dx * fcn(a + (i + 0.5) * dx) for i in range(num_rectangles)])


def trapezoidal(fcn, a, b, num_traps=10):
    dx = (b - a) / num_traps
    y = [fcn(a + i * dx) for i in range(num_traps + 1)]
    return dx * (0.5 * (y[0] + y[-1]) + sum(y[1:len(y) - 1]))


def simpson(fcn, a, b, num=10):
    dx = (b - a) / num
    y = [fcn(a + i * dx) for i in range(num + 1)]
    sub_y = y[1:len(y) - 1]
    return dx * (y[0] + y[-1] + 4.0 * sum(sub_y[::2]) + 2.0 * sum(sub_y[1::2])) / 3.0


def plot_riemann_sum(fcn, a, b, num_rectangles=10, sum_type="middle"):
    if sum_type == "left":
        m = 1.0
        n = 0.0
    elif sum_type == "right":
        m = 0.0
        n = 1.0
    elif sum_type == "middle":
        m = 0.5
        n = 0.5
    else:
        raise ValueError("Invalid sum type '%s'. Expected 'left', 'right', or 'middle'." % sum_type)

    dx = (b - a) / num_rectangles

    x = np.linspace(a, b, 100)
    y = [fcn(v) for v in x]

    result = 0.0
    for i in range(num_rectangles):
        x1 = a + i * dx
        x2 = x1 + dx
        yi = fcn(m * x1 + n * x2)

        result += dx * yi
        plt.plot([x1, x1], [0, yi], 'r')
        plt.plot([x2, x2], [0, yi], 'r')
        plt.plot([x1, x2], [yi, yi], 'r')

    plt.title("%s-sum with N=%d: %.3f" % (sum_type, num_rectangles, result))
    plt.xlabel("x")
    plt.xlabel("y")
    plt.grid(True)
    plt.plot(x, y)
    plt.show()


if __name__ == '__main__':
    f = lambda x: 10 * x - x ** 2.0
    start = 0
    stop = 10
    x = np.linspace(start, stop, 100)
    y = [f(xi) for xi in x]
    print(riemann_sum(f, start, stop, 10))
    print(trapezoidal(f, start, stop, 10))
    print(simpson(f, start, stop, 100))
    plot_riemann_sum(f, start, stop, 100, 'middle')

