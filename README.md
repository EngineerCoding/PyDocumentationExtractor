# PyDocumentExtractor

A simple command line utility which extracts documentation from a set of python files.

Usage can be determined by running
```
python3 PyDocumentExtractor.py -h
```
Outputs:
```
usage: PyDocumentExtractor.py [-h] [-o OUTPUT_DIR] [-r]
                              (-id INPUT_DIR | -f FILE)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The directory to output generated files
  -r, --recursive       Search in the input directory recursively
  -id INPUT_DIR, --input-dir INPUT_DIR
                        The directory to search *.py files to extract
                        documentation from
  -f FILE, --file FILE  The file to extract documentation from
```
