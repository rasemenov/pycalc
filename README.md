# Summary
Python package exporting command-line utility which receives mathematical
expression string as an argument and prints evaluated result:
```shell
$ pycalc '2+2*2'
6
```

Provides following interface:
```shell
$ pycalc --help
usage: pycalc [-h] [-m MODULE [MODULE ...]] EXPRESSION

Pure-python command-line calculator.

optional arguments:
  -h, --help            show this help message and exit
  -m MODULE [MODULE ...], --use-modules MODULE [MODULE ...]
                        additional modules to use
```

Example of output on errors:
```shell
$ pycalc '15(25+1'
ERROR: Someone messed up with brackets: "(1"
```

### Support operations:
* arithmetic (`+`, `-`, `*`, `/`, `//`, `%`, `^`) (`^` is a power)
* comparison (`<`, `<=`, `==`, `!=`, `>=`, `>`)
* built-in python functions (`abs`, `pow`, `round`)
* functions from standard Python module math (trigonometry, logarithms, etc.)
* functions and constants from modules provided with `--use-modules` option
