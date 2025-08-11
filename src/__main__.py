import os, sys, runpy

SRC_DIR = os.path.dirname(__file__)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Default entry: h2f_F01_02_stable/main.py
# Override with: HC2FC_ENTRY=<module> python -m src
module_to_run = os.environ.get("HC2FC_ENTRY", "h2f_F01_02_stable.main")

# Add that package directory so flat imports like `import ui_widgets` work
pkg_parts = module_to_run.split('.')[:-1]
if pkg_parts:
    pkg_dir = os.path.join(SRC_DIR, *pkg_parts)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)

runpy.run_module(module_to_run, run_name="__main__")