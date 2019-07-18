#!/usr/bin/env python
#     Copyright 2019, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python test originally created or extracted from other peoples work. The
#     parts from me are licensed as below. It is at least Free Software where
#     it's copied from other people. In these cases, that will normally be
#     indicated.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import os
import sys

# Find nuitka package relative to us.
sys.path.insert(
    0,
    os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    ),
)

# isort:start

import subprocess
import re

from nuitka.tools.testing.OutputComparison import compareOutput
from nuitka.tools.testing.Virtualenv import withVirtualenv
from nuitka.utils.FileOperations import removeDirectory
from nuitka.tools.testing.Common import createSearchMode, my_print
import nuitka

class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# TODO: Have this in a def main():

# TODO: Put the source clones in os.path joined Appdirs.getCacheDir(), "pypi-git-clones" (AppDirs.py in nuitka/utils)
# git clone if it does not exist
# otherwise git fetch && git reset --hard origin
# normally will not update at all.

# TODO: Get closer to 50 items :)

packages = {
    "chardet": {
        "url": "https://github.com/chardet/chardet.git",
        "requirements_file": None,
        "ignored_tests": None,
    },

    "colorama": {
        "url": "https://github.com/tartley/colorama.git",
        "requirements_file": "requirements-dev.txt",
        "ignored_tests": None,
    },

    "dateutil": {
        "url": "https://github.com/dateutil/dateutil.git",
        "requirements_file": "requirements-dev.txt",
        "ignored_tests": None,
    },

    "idna": {
        "url": "https://github.com/kjd/idna.git",
        "requirements_file": None,
        "ignored_tests": None,
    },

    "jmespath": {
        "url": "https://github.com/jmespath/jmespath.py.git",
        "requirements_file": "requirements.txt",
        "ignored_tests": None,
    },

    "pyasn1": {
        "url": "https://github.com/etingof/pyasn1.git",
        "requirements_file": "requirements.txt",
        "ignored_tests": None,
    },

    "pyyaml": {
        "url": "https://github.com/yaml/pyyaml.git",
        "requirements_file": None,
        "ignored_tests": None,
    },

    "requests": {
        "url": "https://github.com/kennethreitz/requests.git",
        "requirements_file": None,
        "ignored_tests": None,
    },

    "rsa": {
        "url": "https://github.com/sybrenstuvel/python-rsa.git",
        "requirements_file": None,
        "ignored_tests": None,
    },

    "urllib3": {
        "url": "https://github.com/urllib3/urllib3.git",
        "requirements_file": "dev-requirements.txt",
        "ignored_tests": (
            "test/test_no_ssl.py",
        )
    },
}



def main():
    base_dir = os.getcwd()

    search_mode = createSearchMode()

    results = []

    for package_name, details in sorted(packages.items()):
        active = search_mode.consider(dirname=None, filename=package_name)

        if not active:
            continue

        if package_name in (
            "pyyaml", # invalid command 'bdist_nuitka'
        ):
            if search_mode.abortIfExecuted():
                break
            continue

        try:
            with withVirtualenv("venv_%s" % package_name) as venv:
                dist_dir = os.path.join(venv.getVirtualenvDir(), package_name, "dist")

                # setup the virtualenv for testing
                venv.runCommand("git clone %s %s" % (details["url"], package_name))

                # delete ignored tests if any
                if details["ignored_tests"]:
                    for test in details["ignored_tests"]:
                        venv.runCommand("rm %s" % os.path.join(package_name, test))

                cmds = [
                    "python -m pip install pytest",
                    "cd %s" % os.path.join(os.path.dirname(nuitka.__file__), ".."),
                    "python setup.py develop",
                    "cd %s" % os.path.join(venv.getVirtualenvDir(), package_name),
                ]

                if details["requirements_file"]:
                    cmds += [
                        "python -m pip install -r %s" % details["requirements_file"],
                    ]

                # build uncompiled .whl
                cmds += [
                    "python setup.py bdist_wheel",
                ]

                venv.runCommand(
                    commands=cmds
                )

                # install and print out if the active .whl is compiled or not
                venv.runCommand(
                    commands=[
                        "python -m pip install -U %s" % os.path.join(dist_dir, os.listdir(dist_dir)[0]),
                        "python -c print(getattr(__import__('%s'),'__compiled__','__uncompiled_version__'))" % package_name,
                    ]
                )

                # get uncompiled pytest results
                uncompiled_stdout, uncompiled_stderr = venv.runCommandWithOutput(
                    commands=[
                        "cd %s" % package_name,
                        "python -m pytest --disable-warnings",
                    ]
                )

                # build nuitka compiled .whl
                venv.runCommand(
                    commands=[
                        "cd %s" % package_name,
                        "rm -rf dist",
                        "python setup.py bdist_nuitka",
                    ]
                )

                # install and print out if the active .whl is compiled or not
                venv.runCommand(
                    commands=[
                        "python -m pip install -U %s" % os.path.join(dist_dir, os.listdir(dist_dir)[0]),
                        "python -c print(getattr(__import__('%s'),'__compiled__','__uncompiled_version__'))" % package_name,
                    ]
                )

                # get compiled pytest results
                compiled_stdout, compiled_stderr = venv.runCommandWithOutput(
                    commands=[
                        "cd %s" % package_name,
                        "python -m pytest --disable-warnings",
                    ]
                )

        except Exception as e:
            my_print("Package", package_name, "ran into an exception during execution, traceback: ")
            my_print(e)
            if search_mode.abortIfExecuted():
                break
            continue



        os.chdir(base_dir)

        # TODO: currently not working due to permission errors on removing .git files
        removeDirectory(os.path.join(base_dir, "venv_%s" % package_name), ignore_errors=False)

        # compare outputs
        stdout_diff = compareOutput(
            "stdout",
            uncompiled_stdout,
            compiled_stdout,
            ignore_warnings=True,
            ignore_infos=True,
            syntax_errors=True,
        )

        stderr_diff = compareOutput(
            "stderr",
            uncompiled_stderr,
            compiled_stderr,
            ignore_warnings=True,
            ignore_infos=True,
            syntax_errors=True,
        )


        results.append((package_name,stdout_diff,stderr_diff))

        exit_code = stdout_diff or stderr_diff


        my_print(
            bcolors.RED if exit_code else bcolors.GREEN,
            "\n=================================================================================",
            bcolors.ENDC
        )

        my_print(
            bcolors.RED if exit_code else bcolors.GREEN,
            "--- %s ---" % package_name,
            "exit_stdout:",
            stdout_diff,
            "exit_stderr:",
            stderr_diff,
            bcolors.ENDC
        )

        if exit_code:
            my_print(
                bcolors.RED,
                "Error, outputs differed for package %s." % package_name
            )
        else:
            my_print(
                bcolors.GREEN,
                "No differences found for package %s." % package_name
            )

        my_print(
            "=================================================================================\n",
            bcolors.ENDC
        )


        if exit_code != 0 and search_mode.abortOnFinding(dirname=None, filename=package_name):
            break

        if search_mode.abortIfExecuted():
            break

    search_mode.finish()


    # give a summary of all packages

    my_print(
        bcolors.YELLOW,
        "\n\n=====================================SUMMARY=====================================",
        bcolors.ENDC
    )

    for package_name, stdout_diff, stderr_diff in results:
        my_print(
            bcolors.RED if (stdout_diff or stderr_diff) else bcolors.GREEN,
            bcolors.UNDERLINE + package_name + bcolors.ENDC,
            "-",

            bcolors.RED if stdout_diff else bcolors.GREEN,
            "stdout:",
            stdout_diff,
            bcolors.ENDC,

            bcolors.RED if stderr_diff else bcolors.GREEN,
            "stderr:",
            stderr_diff,
            bcolors.ENDC,

            "\n---------------------------------------------------------------------------------"
        )


if __name__ == "__main__":
    main()
