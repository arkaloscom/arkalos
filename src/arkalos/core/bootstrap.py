import importlib.util
import sys
from pathlib import Path

from arkalos.core.path import base_path

def bootstrap():
    bootstrap_path = Path(base_path('app')) / 'bootstrap.py'

    if not bootstrap_path.exists():
        raise FileNotFoundError(f"bootstrap.py not found at {bootstrap_path}")

    spec = importlib.util.spec_from_file_location("bootstrap", str(bootstrap_path))
    bootstrap = importlib.util.module_from_spec(spec)
    sys.modules["bootstrap"] = bootstrap
    spec.loader.exec_module(bootstrap)
    return bootstrap
