#     Copyright 2019, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Outputs to the user.

Printing with intends or plain, mostly a compensation for the print strangeness.

We want to avoid "from __future__ import print_function" in every file out
there, which makes adding another debug print rather tedious. This should
cover all calls/uses of "print" we have to do, and the make it easy to simply
to "print for_debug" without much hassle (braces).

"""

from __future__ import print_function

import sys


def printIndented(level, *what):
    print("    " * level, *what)


def printSeparator(level=0):
    print("    " * level, "*" * 10)


def printLine(*what):
    print(*what)


def printError(message):
    print(message, file=sys.stderr)


def flushStdout():
    sys.stdout.flush()



def my_print(*args, **kwargs):
    """ Make sure we flush after every print.

    Not even the "-u" option does more than that and this is easy enough.

    Use kwarg style=[option] to print in a style listed below
    """

    if "style" in kwargs:
        if kwargs["style"] == "pink":
            style = '\033[95m'
        elif kwargs["style"] == "blue":
            style = '\033[94m'
        elif kwargs["style"] == "green":
            style = '\033[92m'
        elif kwargs["style"] == "yellow":
            style = '\033[93m'
        elif kwargs["style"] == "red":
            style = '\033[91m'
        elif kwargs["style"] == "bold":
            style = '\033[1m'
        elif kwargs["style"] == "underline":
            style = '\033[4m'
        else:
            raise ValueError("%s is an invalid value for keyword argument style" % kwargs["style"])

        del kwargs["style"]

        print(style, *(args + ('\033[0m',)), **kwargs)

    else:
        print(*args, **kwargs)

    flushStdout()
