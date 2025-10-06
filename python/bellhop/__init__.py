
# Import everything to package level

from . import main

__all__ = main.__all__
globals().update({name: getattr(main, name) for name in __all__})

# Was:
#    from .bellhop import *
# but this approach keeps Ruff happy
#
# NB in main.py:
#
#     __all__ = [
#         name for name in globals() if not name.startswith("_")  # ignore private names
#     ]
