import os
import json
from utils import extract_code_slice, format_with_indent, remove_comments

def process_batch_results(result_file, target, output_jsonl):
    """
    Processes the intermediate JSON output from Joern, slices code, 
    aggregates gadgets by file, and writes to the final JSONL output.
    """

    if os.path.exists(result_file):
        print(f"[*] Processing batch results from {result_file}...")
        
        # Aggregation Dictionary: FilePath -> List[Gadgets]
        files_map = {}
        count = 0
        
        # Explicitly use UTF-8 to match WSL output
        with open(result_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    lines_str = record.get("lines", [])
                    if isinstance(lines_str, list) and len(lines_str) > 0:
                            lines = lines_str
                    else:
                            continue

                    # Resolve File Path
                    fname = record['file']
                    if os.path.isfile(target):
                        source_path = target
                    else:
                        source_path = os.path.join(target, fname)
                    
                    if not os.path.exists(source_path):

                        continue

                    # Slice the Code
                    try:
                        gadget_code = extract_code_slice(source_path, lines)
                        
                        # Remove Comments
                        gadget_code = remove_comments(gadget_code)
                        
                        # Format the Code (Indent)
                        gadget_code = format_with_indent(gadget_code)
                        
                        # Create Gadget Object
                        gadget_entry = {
                            "gadget_id": f"{record['method']}_{count}",
                            "label": record['label'],
                            "code_sliced": gadget_code,
                            "raw_lines": lines
                        }
                        
                        # Add to Aggregation Map
                        if source_path not in files_map:
                            files_map[source_path] = []
                        files_map[source_path].append(gadget_entry)
                        
                        count += 1
                        if count % 100 == 0:
                            print(f"[*] Processed {count} gadgets...", end='\r')

                    except Exception as e:
                        print(f"\n[!] Error processing gadget in {fname}: {e}")
                        continue
                        
                except json.JSONDecodeError:
                    print(f"[ERROR] JSON Decode Error: {repr(line)}")

        # Write Aggregated Results to JSONL
        print(f"[*] Writing aggregated data for {len(files_map)} files...")
        try:
            with open(output_jsonl, 'a') as out_f:
                for f_path, gadgets in files_map.items():
                    # Create File-Level Object
                    file_record = {
                        "file_path": f_path,
                        "gadgets": gadgets
                    }
                    out_f.write(json.dumps(file_record) + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to write to {output_jsonl}: {e}")

        print(f"\n[+] Done! Processed {count} gadgets across {len(files_map)} files. Saved to {output_jsonl}")
        
    else:
        print(f"[ERROR] Batch file not found at: {result_file}")
