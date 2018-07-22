from src.mathematics.integrals.integrals import elliptic_k
from src.mathematics.constants.constants import eta0, eps0
from math import pi
import numpy as np

class CoplanarStrips(object):

    def __init__(self, width1=1e-3, height=0.5e-3, gap=0.1e-3, permittivity=9.8, width2=None):
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

        self._w1 = w1
        self._w2 = w2
        self._h = h
        self._s = s
        self._t = t
        self._er_eff = er_eff
        self._z0 = z0

    @property
    def w1(self):
        return self._w1

    @property
    def w2(self):
        return self._w2

    @property
    def h(self):
        return self._h

    @property
    def s(self):
        return self._s

    @property
    def t(self):
        return self._t

    @property
    def er_eff(self):
        return self._er_eff

    @property
    def z0(self):
        return self._z0


if __name__ == '__main__':
    cps = CoplanarStrips(
        width1=300e-6,
        width2=300e-6,
        gap=100e-6,
        height=152e-6,
        permittivity=11.9
    )

    print(cps.z0, cps.er_eff)








