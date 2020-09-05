import shlex
import sys
from subprocess import Popen, PIPE

import importlib_resources
import pkg_resources
from importlib_resources import path
import importlib_resources as ir
from ipython_genutils.py3compat import string_types, bytes_to_str


# taken from https://github.com/jupyter/nbconvert/blob/master/nbconvert/tests/base.py
def run_python(parameters, ignore_return_code=False, stdin=None):
    """
    Run python as a shell command, listening for both Errors and
    non-zero return codes. Returns the tuple (stdout, stderr) of
    output produced during the nbconvert run.
    Parameters
    ----------
    parameters : str, list(str)
        List of parameters to pass to IPython.
    ignore_return_code : optional bool (default False)
        Throw an OSError if the return code
    """
    cmd = [sys.executable]
    if sys.platform == 'win32':
        if isinstance(parameters, string_types):
            cmd = ' '.join(cmd) + ' ' + parameters
        else:
            cmd = ' '.join(cmd + parameters)
    else:
        if isinstance(parameters, string_types):
            parameters = shlex.split(parameters)
        cmd += parameters
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate(input=stdin)
    if not (p.returncode == 0 or ignore_return_code):
        raise OSError(bytes_to_str(stderr))
    return stdout.decode('utf8', 'replace'), stderr.decode('utf8', 'replace')


def main():

    # If the file notebooks-list exists, use it as a definitive list of notebooks to run
    # This in effect ignores any local notebooks you might be working on, so you can run tox
    # without them causing the notebooks task / testenv to fail.
    if importlib_resources.is_resource("notebooks", "notebook-list"):
        print("Using the notebooks-list file to designate which notebooks to run")
        lsNB = [
            sLine for sLine in ir.read_text("notebooks", "notebook-list").split("\n") 
            if len(sLine) > 3 and not sLine.startswith("#")
            ]
    else:
        lsNB = [
            entry for entry in importlib_resources.contents('notebooks') if
                not pkg_resources.resource_isdir('notebooks', entry)
                and entry.endswith(".ipynb")
                ]

    print("Running notebooks:", " ".join(lsNB))

    for entry in lsNB:
        print("*****************************************************************")
        print("Converting and running {}".format(entry))
        print("*****************************************************************")

        with path('notebooks', entry) as file_in:
            out, err = run_python(" -m jupyter nbconvert --execute --to notebook --inplace " + str(file_in))
            sys.stderr.write(err)
            sys.stderr.flush()
            sys.stdout.write(out)
            sys.stdout.flush()

if __name__ == "__main__":
    main()