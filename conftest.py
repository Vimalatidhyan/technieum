"""Root pytest configuration.

Ensures the project root is on sys.path so that
``from backend.db.models import ScanRun`` works in all tests.
"""

import sys
import os

# Add project root to path for absolute imports
sys.path.insert(0, os.path.dirname(__file__))
