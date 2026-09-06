import os
import json
import subprocess
from typing import Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R_SCRIPT_PATH = os.path.join(BASE_DIR, "scripts", "analyze_inventory.R")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")

def run_inventory_analysis(input_file_path: str) -> Dict[str, Any]:
    """
    Executes the R script `analyze_inventory.R` on the provided Excel file.
    Returns structured results and paths to output files.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cmd = [
        "Rscript",
        R_SCRIPT_PATH,
        input_file_path,
        OUTPUT_DIR
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        raise RuntimeError(f"Rscript execution failed: {res.stderr}\nOutput: {res.stdout}")

    json_result_path = os.path.join(OUTPUT_DIR, "analysis_results.json")
    if not os.path.exists(json_result_path):
        raise FileNotFoundError(f"Expected output json file not found at {json_result_path}")

    with open(json_result_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    return results
