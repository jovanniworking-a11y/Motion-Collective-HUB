import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Isolate usage + muse SQLite from services/api/data so a previous smoke
# run cannot change compare means. Must run before app modules import.
_TEST_DATA = Path(tempfile.mkdtemp(prefix="motion-api-test-"))
os.environ["MOTION_DATA_DIR"] = str(_TEST_DATA)
os.environ["DATABASE_URL"] = f"sqlite:///{(_TEST_DATA / 'muse_platform.sqlite3').as_posix()}"
