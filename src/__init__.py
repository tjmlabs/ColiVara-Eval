import os
import glob
import importlib

os.environ["COLIVARA_API_KEY"] = "placeholder"
os.environ["COLIVARA_BASE_URL"] = "https://api.colivara.com"

# Get the directory of the current file
current_dir = os.path.dirname(__file__)

# Get all Python files in the directory, excluding __init__.py
modules = glob.glob(os.path.join(current_dir, "*.py"))
__all__ = [
    os.path.splitext(os.path.basename(f))[0]
    for f in modules
    if os.path.isfile(f) and not f.endswith("__init__.py")
]

# Import all modules
for module in __all__:
    importlib.import_module(f".{module}", package=__name__)
