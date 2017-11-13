import argparse
import importlib.util
import inspect

import os
import sys

ILLEGAL_ATTRIBUTES = ('__builtins__', '__cached__', '__file__', '__loader__',
                      '__name__', '__package__', '__spec__',
                      '__abstractmethods__', '__class__')


def parse_arguments():
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
    if path is None:
        return path
    return os.path.abspath(os.path.expanduser(path))


def analyze_attributes(file_handle, module, class_mode=False):
    for attr_name in dir(module):
        if attr_name not in ILLEGAL_ATTRIBUTES:
            attr = getattr(module, attr_name)
            if attr.__module__ != module.__name__:
                continue
            if inspect.isclass(attr):
                doc = '' if attr.__doc__ is None else attr.__doc__
                file_handle.write('## Class ' + attr_name + '\n' + doc + '\n')
                analyze_attributes(file_handle, attr, class_mode=True)
            elif inspect.isfunction(attr):
                if class_mode:
                    description = '### Method ' + attr_name
                else:
                    description = '## Function ' + attr_name
                doc = '' if attr.__doc__ is None else attr.__doc__
                file_handle.write(description + '\n' + doc + '\n')


def analyze_module(arguments, package, module):
    path = os.path.join(arguments.output_dir, package + '.md')
    with open(path, 'w') as out:
        out.write('# ' + package + '\n' + '\n')
        if module.__doc__:
            out.write(module.__doc__)
        analyze_attributes(out, module)


def extract_from_file(arguments, file=None, prefix=''):
    if file is None:
        file = arguments.file
    if not os.path.isfile(file):
        raise FileNotFoundError(file)
    name, ext = os.path.splitext(os.path.basename(file))
    python_package = prefix + name
    module_spec = importlib.util.spec_from_file_location(
        python_package, location=file)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    analyze_module(arguments, python_package, module)


def extract_from_directory(arguments, dir=None, prefix=''):
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
