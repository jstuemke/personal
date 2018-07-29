from math import sin, pi
from numpy import array


def butterworth_coefficient(index=0, order=1):
    """

    :param index: valid indices are index=1 to index=order
    :param order: The order of the filter
    :return: The ith Butterworth coefficient for a given order
    """
    return 2.0 * sin((2 * index + 1) * pi / (2 * order))


def butterworth_coeffs(order=1):
    """
    :param order:
    :return:  All Butterworth coefficients for a given filter order
    """
    return array([butterworth_coefficient(idx, order) for idx in range(order)])


def butterworth_lpf(cutoff_frequency=1e9, characteristic_impedance=50, order=2):

    kf = 2 * pi * cutoff_frequency
    kz = characteristic_impedance

    g = butterworth_coeffs(order)

    l = []
    c = []
    for idx in range(len(g)):
        if idx % 2:
            l.append(kz * g[idx] / kf)
        else:
            c.append(g[idx] / (kf * kz))

    return l, c

def butterworth_hpf(cutoff_frequency=1e9, characteristic_impedance=50, order=2):
    kf = 2 * pi * cutoff_frequency
    kz = characteristic_impedance

    g = butterworth_coeffs(order)

    l = []
    c = []
    for idx in range(len(g)):
        if idx % 2:
            c.append(1.0 / (g[idx] * kf * kz))
        else:
            l.append(kz / (g[idx] * kf))

    return l, c


def butterworth_bpf(center_frequency=1e9, bandwidth=1e6, characteristic_impedance=50, order=2):
    kf = 2.0 * pi * (bandwidth / 2.0)
    kz = characteristic_impedance
    wc_sq = (2.0 * pi * center_frequency) ** 2
    if order % 2:
        order += 1

    order = int(order / 2)
    g = butterworth_coeffs(order)

    ls = []
    cs = []
    lp = []
    cp = []
    for idx in range(len(g)):
        if idx % 2:
            l = kz * g[idx] / kf
            ls.append(l / 2.0)
            cs.append(2.0 / (wc_sq * l))
        else:
            c = g[idx] / (kz * kf)
            cp.append(c / 2)
            lp.append(2.0 / (wc_sq * c))

    return ls, cs, lp, cp


if __name__ == '__main__':

    ls, cs, lp, cp = butterworth_bpf(center_frequency=4.915e6, bandwidth=400, characteristic_impedance=120, order=4)
    print(ls)
    print(cs)
    print(lp)
    print(cp)