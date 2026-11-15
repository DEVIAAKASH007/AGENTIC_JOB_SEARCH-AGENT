# profile/__init__.py
#
# This package is named 'profile' and shadows the stdlib 'profile' module.
# Python's cProfile module does:
#
#   import profile as _pyprofile
#   run.__doc__ = _pyprofile.run.__doc__
#
# That fails because this package has no 'run' attribute.
#
# Fix: expose the stdlib profile's 'run' function here so cProfile can
# access it without crashing, while keeping this package fully functional.

import sys as _sys
import importlib as _importlib
import importlib.util as _util


def _load_stdlib_profile():
    """Load the stdlib profile module bypassing this package."""
    import os

    # Find the stdlib Lib directory
    stdlib_lib = _sys.base_prefix + "/Lib/profile.py"

    if not os.path.exists(stdlib_lib):
        return None

    spec = _util.spec_from_file_location(
        "_stdlib_profile",
        stdlib_lib
    )

    module = _util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


_stdlib = _load_stdlib_profile()

if _stdlib is not None:
    # Re-export what cProfile needs
    run = _stdlib.run
    runctx = _stdlib.runctx
    Profile = _stdlib.Profile
