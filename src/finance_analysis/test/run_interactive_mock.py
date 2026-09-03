import json
import sys
from pathlib import Path
from unittest.mock import patch

from finance_analysis.main import InteractiveAWSApp

# Add parent directory containing main.py to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Locate the resources directory relative to run_interactive_mock.py
RESOURCES_DIR = Path(__file__).resolve().parent / "resources"


def load_json_mock(filename: str):
    """Load a mock JSON payload from the resources folder."""
    file_path = RESOURCES_DIR / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def mock_aws_data():
    """Mock metrics loaded dynamically from separate JSON files."""
    try:
        mock_cost = load_json_mock("mock_cost.json")
        mock_security = load_json_mock("mock_security.json")
        mock_cloudtrail = load_json_mock("mock_cloudtrail.json")
        return mock_cost, mock_security, mock_cloudtrail
    except FileNotFoundError as e:
        print(f"Error loading mock JSON file: {e}")
        return None, None, None


if __name__ == "__main__":
    app = InteractiveAWSApp()
    a, b, c = mock_aws_data()

    # Patch fetch_aws_metrics to supply mocked telemetry data
    patch.object(app, "fetch_aws_metrics", side_effect=mock_aws_data).start()

    # Launch GUI in full interactive mode with live Ollama calls
    app.mainloop()