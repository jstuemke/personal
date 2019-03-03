
import sys


def is_python_3():
    # type: () -> bool
    """ A function to check if the current version of python is 3.x
    """
    if sys.version_info > (3, 0):
        return True
    else:
        return False
