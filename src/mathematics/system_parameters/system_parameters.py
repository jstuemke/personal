from numpy import array, ndarray, diag, matrix, real, dot, zeros
from numpy.linalg import inv


def _get_f_matrix(z0_list):
    # type: (ndarray) -> ndarray

    f = diag([0.5 / (real(e) ** 0.5) for e in z0_list])

    return f


def z_to_s(z, port_impedances):
    # type: (ndarray, ndarray) -> ndarray

    f = _get_f_matrix(port_impedances)
    g = diag(port_impedances)

    g_herm = g.conjugate().transpose()
    f_inv = inv(f)

    z_gherm = z - g_herm
    z_g_inv = inv(z + g)

    return dot(dot(dot(f, z_gherm), z_g_inv), f_inv)


if __name__ == '__main__':
    z = array([2, 1, 1, 3]).reshape(2, 2)
    z0 = array([50, 100 - 1j * 10])
    print(z_to_s(z, z0))