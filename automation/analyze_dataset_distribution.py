
import json
import glob
import os
import re
from collections import defaultdict

INPUT_DIR = r"c:\Users\KIIT\Desktop\PSU\3rd_Sem\Embedded\prj\gadgets_results"

def analyze_distribution():
    # Stats containers
    dir_stats = defaultdict(lambda: {"total": 0, "vuln": 0, "safe": 0})
    seen_hashes = set()
    
    files = glob.glob(os.path.join(INPUT_DIR, "*.jsonl"))
    print(f"Analyzing {len(files)} files...")
    
    for fpath in files:
        basename = os.path.basename(fpath)
        directory = "unknown"
        if "gadgets_s" in basename:
            directory = basename.split(".")[0].replace("gadgets_", "") # e.g. s01
        
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                entry = json.loads(line)
                
                # Check original path if filename parsing failed (redundant but safe)
                if directory == "unknown":
                    if "\\s0" in entry['file_path']:
                        directory = entry['file_path'].split("\\")[-2] # primitive extraction
                
                for gadget in entry.get('gadgets', []):
                    code = gadget.get('code_sliced', '')
                    label = gadget.get('label')
                    
                    if not code: continue
                    
                    code_sanitized = code
                    code_sanitized = re.sub(r'dataBadBuffer', 'entity_1', code_sanitized, flags=re.IGNORECASE)
                    code_sanitized = re.sub(r'dataGoodBuffer', 'entity_2', code_sanitized, flags=re.IGNORECASE)
                    code_sanitized = re.sub(r'\b\w*[Bb]ad\w*\b', 'func_danger', code_sanitized)
                    code_sanitized = re.sub(r'\b\w*[Gg]ood\w*\b', 'func_safe', code_sanitized)
                    
                    # Dedup Check
                    if code_sanitized in seen_hashes:
                        continue
                    seen_hashes.add(code_sanitized)
                    
                    # Record Stats
                    dir_stats[directory]["total"] += 1
                    if label == 1:
                        dir_stats[directory]["vuln"] += 1
                    else:
                        dir_stats[directory]["safe"] += 1

    print("\n" + "="*60)
    print(f"{'Directory':<10} | {'Total':<8} | {'Vuln (1)':<10} | {'Safe (0)':<10} | {'Vuln %':<8}")
    print("-" * 60)
    
    total_all = 0
    total_vuln = 0
    
    # Sort by directory name
    for d in sorted(dir_stats.keys()):
        stats = dir_stats[d]
        t = stats['total']
        v = stats['vuln']
        s = stats['safe']
        p = (v / t * 100) if t > 0 else 0
        
        total_all += t
        total_vuln += v
        
        print(f"{d:<10} | {t:<8} | {v:<10} | {s:<10} | {p:.1f}%")
        
    print("-" * 60)
    grand_p = (total_vuln / total_all * 100) if total_all > 0 else 0
    print(f"{'GRAND':<10} | {total_all:<8} | {total_vuln:<10} | {(total_all-total_vuln):<10} | {grand_p:.1f}%")
    print("="*60)

if __name__ == "__main__":
    analyze_distribution()
