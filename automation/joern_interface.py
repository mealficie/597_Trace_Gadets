import os
import subprocess
from utils import win_to_wsl_path
from config import JOERN_SCRIPT_WSL_PATH

def run_joern_wsl(input_file_path):
    """
    Invokes Joern inside WSL to process the given file.
    """
    # Convert input path to WSL
    wsl_input_path = win_to_wsl_path(os.path.abspath(input_file_path))

    # Temporary output file for this batch (Absolute path shared between Win/WSL)
    # Use the same directory as input file for simplicity (mapped to /mnt/...)
    temp_out_wsl = f"{os.path.dirname(wsl_input_path)}/batch_gadgets.json"
    temp_out_win = os.path.dirname(os.path.abspath(input_file_path)) + "\\batch_gadgets.json"
    
    cmd = [
        "wsl",
        "joern",
        "--script", JOERN_SCRIPT_WSL_PATH,
        "--param", f"inputPath={wsl_input_path}",
        "--param", f"outFile={temp_out_wsl}"
    ]
    
    print(f"[*] Analyzing: {input_file_path}...")
    try:
        subprocess.run(cmd, check=True, text=True) # Output captured by stdout
        return temp_out_win
    except subprocess.CalledProcessError as e:
        print(f"[!] Joern failed: {e}")
        return None
