

class _BaseClass(object):
    """ A Dummy class for type data

    """

    def __init__(self):
        # type: () -> None
        """ A dummy constructor for type data

        """
        pass


class _NestClass(_BaseClass):
    """ A Dummy class for type data

    """

    def __init__(self):
        # type: () -> None
        """ a dummy constructor for type data

        """
        _BaseClass.__init__(self)


# Define a nested class
_NestClass = _NestClass()
# get the nested class type
NestClassType = type(_NestClass)
# get the nested.__class__ type
NestClassClassType = type(_NestClass.__class__)
