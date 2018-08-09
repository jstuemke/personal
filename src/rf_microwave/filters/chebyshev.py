from src.rf_microwave.filters.butterworth import butterworth_coefficient as bw
from math import sin, sinh, atanh, sqrt, pi
from numpy import array


def _pi_network_z_parameters(z1, z2, z3):

    k = z1 * z3 / (z1 + z2 + z3)

    k1 = 1.0 + z2 / z3
    k2 = 1.0 + z2 / z1

    return k * array([k1, 1.0, 1.0, k2]).reshape(2, 2)


def _l_network_z_parameters(z1, z2, shunt_first=True):

    if not shunt_first:
        raise NotImplementedError("Series-First has not yet been implemented")

    return array([z1, z1, z1, z1 + z2]).reshape(2, 2)



def chebyshev_coeffs(order=1, ripple=0.2):
    """

    :param index:
    :param order:
    :param ripple:
    :return:
    """
    a = 10.0 ** (ripple / 10.0) - 1.0
    b = sinh(atanh(1.0 / sqrt(1 + a)) / order)

    c = [bw(0, order) / b]

    for m in range(1, order):
        top = bw(m, order) * bw(m - 1, order) / c[m - 1]
        bottom = b ** 2 + (sin(m * pi / order)) ** 2
        c.append(top / bottom)

    return array(c)


def chebyshev_lpf(cutoff_frequency=1e9, ripple=0.2, characteristic_impedance=50, order=2):

    kf = 2 * pi * cutoff_frequency
    kz = characteristic_impedance

    g = chebyshev_coeffs(order, ripple=ripple)

    l = []
    c = []
    for idx in range(len(g)):
        if idx % 2:
            l.append(kz * g[idx] / kf)
        else:
            c.append(g[idx] / (kf * kz))

    return l, c


def chebyshev_hpf(cutoff_frequency=1e9, ripple=0.2, characteristic_impedance=50, order=2):
    kf = 2 * pi * cutoff_frequency
    kz = characteristic_impedance

    g = chebyshev_coeffs(order, ripple=ripple)

    l = []
    c = []
    for idx in range(len(g)):
        if idx % 2:
            c.append(1.0 / (g[idx] * kf * kz))
        else:
            l.append(kz / (g[idx] * kf))

    return l, c


def chebyshev_bpf(center_frequency=1e9, bandwidth=1e6, ripple=0.2, characteristic_impedance=50, order=2):
    kf = 2.0 * pi * (bandwidth / 2.0)
    kz = characteristic_impedance
    wc_sq = (2.0 * pi * center_frequency) ** 2

    g = chebyshev_coeffs(order, ripple=ripple)

    # order is shunt C, shunt L, series L, series C
    values = []
    for idx in range(len(g)):
        if idx % 2:
            l = kz * g[idx] / kf
            values.append(l / 2.0)
            values.append(2.0 / (wc_sq * l))
        else:
            c = g[idx] / (kz * kf)
            values.append(c / 2)
            values.append(2.0 / (wc_sq * c))

    return values

# STEP 1: COMPUTE g-Values

# STEP 2: TRANSFORM FROM LPF TO HPF, BPF, or BRF IF DESIRED
# High Pass: L's become C's with value L = 1/C, C's become L's with value 1/L
# Band Pass: L's become series tank with Lt = L/2 & Ct = 2 / wc^2L,  C's become parallel tank with Cp = C/2 & Lp = 2 / wc^2C

# STEP 3: SCALE TO FREQUENCY
# kf = w_desired / w_reference = f_desired / f_reference
# L = L_reference / kf
# C = C_reference / kf

# STEP 4: SCALE TO IMPEDANCE
# kz = Z_desired / Z_reference
# R = kz * R_reference
# L = kz * L_reference / kf
# C = C_reference / (kf * kz)


if __name__ == '__main__':
    bpf = chebyshev_bpf(center_frequency=5e9, bandwidth=100e6, ripple=0.2, characteristic_impedance=50, order=5)
    print(bpf)



