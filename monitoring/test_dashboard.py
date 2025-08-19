# monitoring/test_dashboard.py
import subprocess

def test_dashboard_runs():
    """
    Simple test: try launching Streamlit with --help to confirm it's installed and callable.
    """
    result = subprocess.run(
        ["streamlit", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout