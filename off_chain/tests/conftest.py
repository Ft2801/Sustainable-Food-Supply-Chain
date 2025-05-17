# Add the project root to Python path for imports
import os
import sys

# Get the absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to Python path if it's not already there
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
