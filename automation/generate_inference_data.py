
import os
import sys
import json
import argparse
from joern_interface import run_joern_wsl
from utils import extract_code_slice, format_with_indent, remove_comments

def generate_inference_data(target_path):
    target_path = os.path.abspath(target_path)
    if not os.path.exists(target_path):
        print(f"[!] Target not found: {target_path}")
        return

    print(f"[*] Starting Inference Extraction for: {target_path}")    
    intermediate_json = run_joern_wsl(target_path)
    
    if not intermediate_json or not os.path.exists(intermediate_json):
        print("[!] Joern execution failed or produced no output.")
        return

    final_output = "inference_ready.jsonl"
    print(f"[*] Processing gadgets into {final_output}...")
    
    gadgets_found = 0
        
    with open(final_output, 'w', encoding='utf-8') as outfile:
        with open(intermediate_json, 'r', encoding='utf-8', errors='replace') as infile:
            for line in infile:
                if not line.strip(): continue
                try:
                    record = json.loads(line)                    
                    fname = record.get('file')
                    if os.path.isfile(target_path):
                        source_path = target_path
                    else:
                        source_path = os.path.join(target_path, fname)
                        
                    if not os.path.exists(source_path):
                        continue
                        
                    lines = record.get("lines", [])
                    if not lines: continue
                    
                    raw_code = extract_code_slice(source_path, lines)
                    raw_code = remove_comments(raw_code)
                    raw_code = format_with_indent(raw_code)
                    
                    if not raw_code.strip(): continue

                    model_input = {
                        "instruction": "You are a secure code analysis assistant. Analyze the following C/C++ code snippet for Stack-Based Buffer Overflow (CWE-121). Respond with 'Vulnerable' if the code contains a buffer overflow, or 'Safe' if it is secure.",
                        "input": raw_code,
                        "output": ""
                    }
                    
                    outfile.write(json.dumps(model_input) + "\n")
                    gadgets_found += 1
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"[!] Error processing gadget: {e}")
                    continue
                
    print(f"[*] Success! {gadgets_found} gadgets ready for inference.")
    print(f"    -> Output File: {os.path.abspath(final_output)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate inference data using Joern.")
    parser.add_argument("target", help="Path to C file or directory")
    args = parser.parse_args()
    
    generate_inference_data(args.target)
