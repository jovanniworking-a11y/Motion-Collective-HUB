import sys
from pathlib import Path

# The bridge, the mock API and the zone counter live one level up.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
