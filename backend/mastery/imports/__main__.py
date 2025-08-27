# Do Django setup *before* importing CLI to avoid settings errors.
import os, sys
from pathlib import Path
import django

BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from .cli import main

if __name__ == "__main__":
    main()
