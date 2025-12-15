
import json
import glob
import random
import os

# Configuration
INPUT_DIR = r"c:\Users\KIIT\Desktop\PSU\3rd_Sem\Embedded\prj\gadgets_results"
OUTPUT_DIR = r"c:\Users\KIIT\Desktop\PSU\3rd_Sem\Embedded\prj\dataset"
TRAIN_RATIO = 0.8
SEED = 42

def prepare_dataset():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_gadgets = []
    seen_hashes = set()
    
    # 1. Gather all JSONL files
    files = glob.glob(os.path.join(INPUT_DIR, "*.jsonl"))
    print(f"[*] Found {len(files)} gadget files.")
    
    for fpath in files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    entry = json.loads(line)
                    
                    # Process each gadget in the file
                    for gadget in entry.get('gadgets', []):
                        code = gadget.get('code_sliced', '')
                        label = gadget.get('label')
                        
                        if not code: continue
                        
                        # 2. Sanitization: Mask "cheating" keywords (bad/good names) using regex
                        # We want to remove hints like 'badSink', 'dataBadBuffer', 'goodG2B'
                        # Replace them with neutral terms to force model to learn logic.
                        
                        # Replace variable/function names containing "bad" (case insensitive) -> "func_1" or "var_1"
                        # We use a simple approach: if it looks like an identifier containing 'bad', replace it.
                        # Note: This is a heuristics-based approach.
                        import re
                        
                        # Masking Strategy:
                        # 1. 'dataBadBuffer' -> 'buffer_A'
                        # 2. 'dataGoodBuffer' -> 'buffer_B'
                        # 3. '...badSink' -> 'sink_function'
                        # 4. '...goodG2B...' -> 'helper_function'
                        
                        code_sanitized = code
                        # Specific variable replacements common in Juliet
                        code_sanitized = re.sub(r'dataBadBuffer', 'entity_1', code_sanitized, flags=re.IGNORECASE)
                        code_sanitized = re.sub(r'dataGoodBuffer', 'entity_2', code_sanitized, flags=re.IGNORECASE)
                        
                        # Generic function calls with 'bad' or 'good' in them
                        code_sanitized = re.sub(r'\b\w*[Bb]ad\w*\b', 'func_danger', code_sanitized)
                        code_sanitized = re.sub(r'\b\w*[Gg]ood\w*\b', 'func_safe', code_sanitized)
                        
                        # 3. Deduplication
                        # Use a hash of the sanitized code to avoid duplicates
                        if code_sanitized in seen_hashes:
                            continue
                        seen_hashes.add(code_sanitized)

                        # 4. Format as Instruction Tuning Data
                        instruction = (
                            "You are a secure code analysis assistant. "
                            "Analyze the following C/C++ code snippet for Stack-Based Buffer Overflow. "
                            "Respond with 'Vulnerable' if the code contains a buffer overflow, or 'Safe' if it is secure."
                        )
                        
                        output_text = "Vulnerable" if label == 1 else "Safe"
                        
                        data_point = {
                            "instruction": instruction,
                            "input": code_sanitized,
                            "output": output_text
                        }
                        
                        all_gadgets.append(data_point)
                        
        except Exception as e:
            print(f"[!] Error reading {fpath}: {e}")

    print(f"[*] Total gadgets collected: {len(all_gadgets)}")
    
    # 3. Shuffle
    random.seed(SEED)
    random.shuffle(all_gadgets)
    
    # 4. Split
    split_idx = int(len(all_gadgets) * TRAIN_RATIO)
    train_data = all_gadgets[:split_idx]
    test_data = all_gadgets[split_idx:]
    
    # 5. Save
    train_path = os.path.join(OUTPUT_DIR, "train.jsonl")
    test_path = os.path.join(OUTPUT_DIR, "test.jsonl")
    
    with open(train_path, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")
            
    with open(test_path, 'w', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item) + "\n")
            
    print(f"[*] Dataset Export Complete:")
    print(f"    - Train: {len(train_data)} items -> {train_path}")
    print(f"    - Test:  {len(test_data)} items  -> {test_path}")

if __name__ == "__main__":
    prepare_dataset()
