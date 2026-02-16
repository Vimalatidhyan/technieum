"""Root conftest.py for reconx-enterprise tests.

Ensures backend package is importable from the reconx-enterprise directory.
"""

import sys
import os

# Add the reconx-enterprise directory to sys.path so 'from backend.db...' works
sys.path.insert(0, os.path.dirname(__file__))
