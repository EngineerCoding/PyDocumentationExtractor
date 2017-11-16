"""
Loads module(s) and gets the documentation off it and outputs it in a
very simple MarkDown file.
"""

import argparse
import importlib.util
import inspect

import os
import sys

ILLEGAL_ATTRIBUTES = ('__builtins__', '__cached__', '__file__', '__loader__',
                      '__name__', '__package__', '__spec__',
                      '__abstractmethods__', '__class__')


def parse_arguments():
    """ Sets up the argument parser to get command line arguments.

    Returns:
          Namespace: A namespace object returned by the parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-dir', default='./',
                        help='The directory to output generated files')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Search in the input directory recursively')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-id', '--input-dir',
                       help='The directory to search *.py files to extract '
                            'documentation from')
    group.add_argument('-f', '--file',
                       help='The file to extract documentation from')
    return parser.parse_args()


def local_to_abs_path(path):
    """ Converts a local file path to an absolute file path.

    Arguments:
        path (string): The local file path
    Returns:
        string: The absolute file path
    """
    if path is None:
        return path
    return os.path.abspath(os.path.expanduser(path))


def get_formatted_parameters(func):
    """ Gets the parameters of a function and formats those in a pretty way
    so it represents the almost equal parameter definition.

    Arguments:
         func (callable): The callable to get the parameters from
    Returns:
        string: The string which represents the parameter definition as
            typed in the source code.
    """
    signature = inspect.signature(func, follow_wrapped=False)
    formatted_parameters = '('
    parameter_names = list(signature.parameters.keys())
    for i in range(len(parameter_names)):
        formatted_parameters += str(signature.parameters[parameter_names[i]])
        if i != len(parameter_names) - 1:
            formatted_parameters += ', '
    return formatted_parameters + ')'


def analyze_attributes(file_handle, module, class_mode=False):
    """ Analyzes the attributes of a module by checking whether the attributes
    are classes or functions. When it are functions the content is directly
    written to the markdown file, but when it is a class it will call this
    function recursively with class_mode set to True to check for sub methods.

    Arguments:
        file_handle (file): A file like object which has at least the write
            method.
        module: An actual python module when class_mode is set to False. This
            should represent a class when class_mode is set to True
        class_mode (bool): A boolean indicating whether module is an actual
            module (False) or class (True)
    """
    for attr_name in dir(module):
        if attr_name not in ILLEGAL_ATTRIBUTES:
            attr = getattr(module, attr_name)
            module_name = getattr(attr, '__module__', '')
            if module_name != module.__name__:
                continue
            if inspect.isclass(attr):
                doc = '' if attr.__doc__ is None else attr.__doc__
                file_handle.write('## Class ' + attr_name + '\n' + doc + '\n')
                analyze_attributes(file_handle, attr, class_mode=True)
            elif inspect.isfunction(attr):
                if class_mode:
                    description = '### Method ' + attr_name
                else:
                    description = ('## Function ' + attr_name +
                                   get_formatted_parameters(attr))
                doc = '' if attr.__doc__ is None else attr.__doc__
                file_handle.write(description + '\n' + doc + '\n')


def analyze_module(arguments, package, module):
    """ Creates the markdown file using the package name and output directory.
    This also writes the global documentation of a module to the file, and
    then it will call analyze_attributes to get the actual functions in the
    module.

    Arguments:
         arguments (Namespace): A Namespace object as produced by an
            ArgumentParser which needs the output_dir attribute.
         package (string): The name of the current package.
         module: The module to analyze
    """
    path = os.path.join(arguments.output_dir, package + '.md')
    with open(path, 'w') as out:
        out.write('# ' + package + '\n' + '\n')
        if module.__doc__:
            out.write(module.__doc__)
        analyze_attributes(out, module)


def extract_from_file(arguments, file=None, prefix=''):
    """ Extracts documentation from a file using extract_module. When the file
    argument is set to None, it will retrieve the file attribute of the
    arguments argument. When the file does not exist, this will raise a
    FileNotFoundError.

    Arguments:
        arguments (Namespace): A Namespace object as produced by an
            ArgumentParser which needs the file attribute.
        file (string): A path to a file or None
        prefix (string): The prefix used while traversing a directory.
    """
    if file is None:
        file = arguments.file
    if not os.path.isfile(file):
        raise FileNotFoundError(file)
    name, ext = os.path.splitext(os.path.basename(file))
    python_package = prefix + name
    # Load the module
    module_spec = importlib.util.spec_from_file_location(
        python_package, location=file)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    analyze_module(arguments, python_package, module)


def extract_from_directory(arguments, dir=None, prefix=''):
    """ This will traverse a directory for python files. When recursive mode
    is turned on, this will also traverse sub directories.

    Arguments:
        arguments (Namespace): A Namespace object as produced by an
            ArgumentParser which needs the recursive attribute.
        dir (string): A path to a directory to traverse.
        prefix (string): The prefix used while traversing a directory
    """
    if not os.path.isdir(dir):
        raise NotADirectoryError(dir)
    for sub_path in os.listdir(dir):
        path = os.path.join(dir, sub_path)
        if os.path.isfile(path) and path.endswith('.py'):
            extract_from_file(arguments, file=path, prefix=prefix)
        elif arguments.recursive and os.path.isdir(path):
            extract_from_directory(arguments, dir=path,
                                   prefix=prefix + sub_path + '.')


def main():
    arguments = parse_arguments()
    arguments.output_dir = local_to_abs_path(arguments.output_dir)
    arguments.file = local_to_abs_path(arguments.file)
    if arguments.input_dir is not None:
        arguments.input_dir = local_to_abs_path(arguments.input_dir)
        sys.path.append(arguments.input_dir)
        extract_from_directory(arguments, dir=arguments.input_dir)
    else:
        arguments.file = local_to_abs_path(arguments.file)
        extract_from_file(arguments)


if __name__ == '__main__':
    main()
