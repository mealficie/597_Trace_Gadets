import os
from utils import win_to_wsl_path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Project Root is the parent of automation/
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Absolute Path to the Scala script (in Windows format)
JOERN_SCRIPT_WIN_PATH = os.path.join(SCRIPT_DIR, "query_gadgets.sc")

# Convert to WSL path for Joern
JOERN_SCRIPT_WSL_PATH = win_to_wsl_path(JOERN_SCRIPT_WIN_PATH)

# Output Directory
RESULTS_DIR = os.path.join(PROJECT_ROOT, "gadgets_results")
