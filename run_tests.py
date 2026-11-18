"""Run the plain test functions with the standard library and an isolated database."""
import importlib.util
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

import src.session as session


def main():
    random.seed(20261110)
    suite = unittest.TestSuite()
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="poker-tests-") as temp:
        with patch.object(session, "DB_FILE", str(Path(temp) / "session.db")):
            for path in sorted((root / "tests").glob("test_*.py")):
                spec = importlib.util.spec_from_file_location(path.stem, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "DB_FILE"):
                    module.DB_FILE = session.DB_FILE
                for name, test in sorted(vars(module).items()):
                    if name.startswith("test_") and callable(test):
                        suite.addTest(unittest.FunctionTestCase(test, description=f"{path.name}::{name}"))
            result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
