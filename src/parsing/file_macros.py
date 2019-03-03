
import io
import os
from csv import reader

from backports_abc import Generator
import src.compatibility.python3_compatibility as check


class FileDataObject(object):
    """ FileDataObject Class

    :Synopsis: a class to contain file data found

    """

    def __init__(self, folder_path, file_name):
        # type: (str, str) -> None
        """ Constructor

        :param folder_path: the folder path to the file
        :param file_name: the file name
        """

        self.folder_path = None
        self.file_name = None

        self.set(
            folder_path=folder_path,
            file_name=file_name
        )

    def set(self, folder_path, file_name):
        # type: (str, str) -> None
        """ set the object values

        :param folder_path: folder path for the object
        :param file_name:  file name of the object
        """
        self.folder_path = folder_path
        self.file_name = file_name

    def get_path(self):
        # type: () -> str
        """ return the object path

        :return: the object path
        """
        return os.path.join(self.folder_path, self.file_name)

    def get_base(self, extension=None, prefix=None, postfix=None):
        # type: (str or None,str or None, str or None) -> str
        """ get the filename without any extension
        :param extension: Optional parameter to appended a extension to the end of the base name
        :param prefix: Optional parameter to add a string before the base name
        :param postfix: Optional parameter to add a string after the base name but before the extension
        :return:
        """

        base_name = os.path.splitext(self.file_name)[0]

        if prefix is not None:
            base_name = "%s%s" % (prefix, base_name)

        if postfix is not None:
            base_name = "%s%s" % (base_name, postfix)

        if extension is None or extension == "":
            return base_name
        else:
            return "%s.%s" % (base_name, extension)


def parse_line_by_comma(file_object, escape_comma=True):
    # type: ([str], bool) -> [str]
    """ Line parsing generator for csv segmentation

    :param escape_comma: Apply a escape string sequence to handle comma within quotes within a csv file
    :param file_object: the file object generator
    :return: array of split objects
    """

    for line in file_object:
        line = line.strip()

        if line is None:
            continue

        if line == "":
            continue

        if escape_comma:
            if "\"" in line:
                if check.is_python_3():
                    line_object = io.StringIO(line)
                else:
                    line_object = io.BytesIO(line)

                for item in reader(line_object, delimiter=','):
                    yield item
                    break
            else:
                yield line.split(",")

        else:
            yield line.split(",")


def makefolder(input_path, usedirname=True):
    # type: (str,bool) -> bool
    """ A macro to quickly make a folder if a folder does not exist

    :param usedirname: split the dir from the file path
    :param input_path: the folder path

    """
    if usedirname:
        input_dir = os.path.dirname(input_path)
    else:
        input_dir = input_path

    if not os.path.exists(input_dir):
        # noinspection PyBroadException
        try:
            os.makedirs(input_dir)
        except:
            return False
    return True


def exists_within(file_extensions, folder_path):
    # type: ([str], str) -> Generator[FileDataObject]
    """ file generator that returns only file types of a given file extension

    :Synopsis: a generator that returns only file types of a given extension

    :param file_extensions: the file extension to find (as array)
    :param folder_path: a folder path

    :return: FileDataObject
    """

    for walk_result in os.walk(folder_path):
        dirpath, dirnames, filenames = walk_result
        for filename in filenames:
            if filename.endswith(tuple(file_extensions)):
                yield FileDataObject(
                    folder_path=dirpath,
                    file_name=filename
                )


def exists_within_fast(file_extensions, folder_path):
    # type: ([str], str) -> Generator[FileDataObject]
    """ file generator that returns only file types of a given file extension

    :Synopsis: a generator that returns only file types of a given extension

    :param file_extensions: the file extension to find (as array)
    :param folder_path: a folder path

    :return: FileDataObject
    """
    import scandir

    for walk_result in scandir.walk(folder_path):
        dirpath, dirnames, filenames = walk_result
        for filename in filenames:
            if filename.endswith(tuple(file_extensions)):
                yield FileDataObject(
                    folder_path=dirpath,
                    file_name=filename
                )