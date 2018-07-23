from src.mathematics.integrals.integrals import elliptic_k
from src.mathematics.constants.constants import eta0, eps0
from matplotlib import pyplot as plt
from math import pi
import numpy as np


def coplanar_strips(
        width1=1e-3,
        height=0.5e-3,
        gap=0.1e-3,
        permittivity=9.8,
        width2=None
):
    if width2 is None:
        width2 = width1

    w1 = width1
    w2 = width2
    h = height
    s = gap
    er = permittivity

    d = w1 + s
    b = w2 + s

    k = ((1.0 + b / d - s / d) * (s / b)) ** 0.5
    kp = (1 - k ** 2) ** 0.5

    e_k = elliptic_k(k)
    e_kp = elliptic_k(kp)
    cp1 = 2 * eps0 * e_kp / e_k

    l1 = (pi / 2) * (2.0 * b / h - s / h)
    l2 = pi * s / (2 * h)
    l3 = (pi / 2) * (2.0 * d / h - s / h)
    l = [l1, l2, l3]

    t = np.divide(np.exp(l) - 1, np.exp(l) + 1)
    k1_sq = (t[0] - t[1]) * (t[2] - t[1]) / ((t[0] + t[1]) * (t[2] + t[1]))
    k1 = k1_sq ** 0.5
    k1p = (1 - k1_sq) ** 0.5

    e_k1 = elliptic_k(k1)
    e_k1p = elliptic_k(k1p)
    cp2 = eps0 * (er - 1) * e_k1 / e_k1p

    er_eff = 1 + cp2 / cp1

    z0 = eta0 * e_k / (2 * e_kp * er_eff ** 0.5)
    return z0, er_eff


if __name__ == '__main__':
    sweep = np.linspace(100e-6, 500e-6, 10)

    cps = [
        coplanar_strips(
            width1=200e-6,
            width2=None,
            gap=100e-6,
            height=s,
            permittivity=11.8
        ) for s in sweep
    ]

    z0, er = zip(*cps)
    plt.plot(sweep * 1e6, z0)
    plt.show()















