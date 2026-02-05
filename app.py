import sys
from pathlib import Path

# Add the src directory to the system path so Python can find your module
src_path = str(Path(__file__).parent / "wildfire-risk-dashboard" / "src")
if src_path not in sys.path:
    sys.path.append(src_path)