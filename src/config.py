from pathlib import Path

# Default Configuration
PROJECT_ROOT = str(Path(__file__).parent.parent)

# Customizable Configuration
NODE_PATH = "/home/cloudsky/Research/Autoware/autoware/src/universe/autoware.universe/perception/detected_object_validation"  # NODE_PATH = f"{PROJECT_ROOT}/demo_nodes/perception/detected_object_validation"
GENERATE_MODE = "new"  # "overwrite" or "new"
GENERATE_PATH = f"{PROJECT_ROOT}/generated_nodes/"
