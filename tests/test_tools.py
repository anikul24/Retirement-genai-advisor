# tests/test_tools.py
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
print (f"Project root for tests: {project_root}")

if project_root not in sys.path:
    sys.path.append(project_root)

from src.tools_math import _calculate_retirement_growth, _calculate_rmd

def test_calculator_fv():
    """Regression Test: Verify Future Value math is exact."""
    # Scenario: $10k principal, $1k/year, 10 years, 10% return
    # Expected result should be roughly calculated or matched to a known value
    result = _calculate_retirement_growth(10000, 1000, 10, 0.10)
    
    # Check if the output string contains the correct dollar amount
    # (FV approx $41,874)
    assert "$41,874" in result or "$41,875" in result

def test_rmd_logic():
    """Regression Test: Verify RMD logic for age < 73."""
    result = _calculate_rmd(70, 500000)
    assert "not required" in result.lower()