from .production import *
try:
    from .local import *
except ImportError:
    print('No local.py was found. You must be on production.')
