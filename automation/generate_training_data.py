import os
import sys
from config import RESULTS_DIR
from joern_interface import run_joern_wsl
from processor import process_batch_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_training_data.py <path_to_c_file_or_directory>")
        sys.exit(1)
        
    target = os.path.abspath(sys.argv[1])
    
    # Determine Output Filename
    target_name = os.path.basename(target)
    if not target_name: # Handle case where target ends with slash
        target_name = os.path.basename(os.path.dirname(target))
        
    output_filename = f"gadgets_{target_name}.jsonl"
    
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    output_jsonl_path = os.path.join(RESULTS_DIR, output_filename)
    
    print(f"[*] Results will be saved to: {output_jsonl_path}")
    
    # Cleanup previous run for this specific target
    if os.path.exists(output_jsonl_path):
        os.remove(output_jsonl_path)

    # Run Joern ONCE on the target (File or Directory)
    result_file = run_joern_wsl(target)
    
    if result_file:
        process_batch_results(result_file, target, output_jsonl_path)
    else:
        print("[!] Joern execution failed.")

if __name__ == "__main__":
    main()
