import numpy as np
from numpy.linalg import inv

_tol = 100 * np.finfo(np.float).eps


def _get_f_matrix(z0_list):
    # type: (np.ndarray) -> np.ndarray

    f = np.diag([0.5 / (np.real(e) ** 0.5) for e in z0_list])

    return f


def z_to_s(z, port_impedances=None):
    # type: (np.ndarray, np.ndarray) -> np.ndarray

    z = np.array(z, dtype=complex)
    if port_impedances is None:
        port_impedances = np.array([50.0 for _ in range(len(z))])

    f = _get_f_matrix(port_impedances)
    g = np.diag(port_impedances)

    g_herm = g.conjugate().transpose()
    f_inv = inv(f)

    z_gherm = z - g_herm
    z_g_inv = inv(z + g)

    ret = np.dot(np.dot(np.dot(f, z_gherm), z_g_inv), f_inv)
    ret.real[abs(ret.real) < _tol] = 0.0
    ret.imag[abs(ret.imag) < _tol] = 0.0

    return ret


def s_to_z(s, port_impedances=None):
    # type: (np.ndarray, np.ndarray) -> np.ndarray

    s = np.array(s, dtype=complex)
    if port_impedances is None:
        port_impedances = np.array([50.0 for _ in range(len(z))])

    f = _get_f_matrix(port_impedances)
    g = np.diag(port_impedances)
    identity = np.diag([1 for _ in range(len(s))])
    g_herm = g.conjugate().transpose()
    f_inv = inv(f)

    a = inv(identity - s)
    b = np.dot(s, g) + g_herm

    ret = np.dot(np.dot(np.dot(f_inv, a), b), f)
    ret.real[abs(ret.real) < _tol] = 0.0
    ret.imag[abs(ret.imag) < _tol] = 0.0

    return ret


def z_to_y(z):

    return inv(z)


def y_to_z(y):

    return inv(y)


def _casecade_z(z1, z2):
    z11_1 = z1[1 - 1, 1 - 1]
    z12_1 = z1[1 - 1, 2 - 1]
    z21_1 = z1[2 - 1, 1 - 1]
    z22_1 = z1[2 - 1, 2 - 1]

    z11_2 = z2[1 - 1, 1 - 1]
    z12_2 = z2[1 - 1, 2 - 1]
    z21_2 = z2[2 - 1, 1 - 1]
    z22_2 = z2[2 - 1, 2 - 1]

    k = z11_2 + z22_1
    z11 = z11_1 - z12_1 * z21_1 / k
    z22 = z22_2 - z12_2 * z21_2 / k

    z12 = z12_1 * k / z12_2
    z21 = z21_2 * k / z21_1

    return np.array([z11, z12, z21, z22]).reshape(2, 2)


def two_port_cascade_z(z_list):
    z_current = z_list[0]
    for idx in range(1, len(z_list)):
        z_current = _casecade_z(z_current, z_list[idx])

    return z_current

def two_port_t_to_s(t):
    """
    According to Dean A. Frickey: 'Conversions Between S, Z, Y, h, ABCD, and T Parameters which are Valid for Complex
    Source and Load Impedances'.

    :param t:
    :return:
    """

    if len(t) != 2:
        raise ValueError("Unable to convert T-Parameters to S-Parameters for dimension: %d" % len(t))

    t11 = t[1 - 1, 1 - 1]
    t12 = t[1 - 1, 2 - 1]
    t21 = t[2 - 1, 1 - 1]
    t22 = t[2 - 1, 2 - 1]

    dt = t11 * t22 - t12 * t21
    s11 = t21 / t11
    s12 = dt / t11
    s21 = 1.0 / t11
    s22 = -t12 / t11

    return np.array([s11, s12, s21, s22]).reshape(2, 2)


def two_port_s_to_t(s):

    """
    According to Dean A. Frickey: 'Conversions Between S, Z, Y, h, ABCD, and T Parameters which are Valid for Complex
    Source and Load Impedances'.

    :param s:
    :return:
    """

    if len(s) != 2:
        raise ValueError("Unable to convert S-Parameters to T-Parameters for dimension: %d" % len(s))

    s11 = s[1 - 1, 1 - 1]
    s12 = s[1 - 1, 2 - 1]
    s21 = s[2 - 1, 1 - 1]
    s22 = s[2 - 1, 2 - 1]

    ds = s12 * s21 - s11 * s22
    t11 = 1.0 / s21
    t12 = -s22 / s21
    t21 = s11 / s21
    t22 = ds / s21

    return np.array([t11, t12, t21, t22]).reshape(2, 2)


if __name__ == '__main__':
    z = np.array([2, 1, 1, 2]).reshape(2, 2)
    z0 = np.array([50, 50])

    print(_casecade_z(z, z))
    print("or")
    print(two_port_cascade_z([z, z, z, z]))

