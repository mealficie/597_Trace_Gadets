import os
import subprocess
import re

def remove_comments(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " 
        else:
            return s 
            
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def win_to_wsl_path(win_path):
    """
    Converts a Windows absolute path to a WSL /mnt/... path.
    """
    if ":" in win_path:
        drive, rest = win_path.split(":", 1)
        rest = rest.replace('\\', '/')
        return f"/mnt/{drive.lower()}{rest}"
    return win_path.replace('\\', '/')

def format_with_indent(code):
    """
    Formats the given C code string using GNU Indent via WSL.
    Uses 'indent -st' to read from stdin and write to stdout.
    """
    if not code or not code.strip():
        return code

    try:
        # -kr: K&R style, -i4: 4 spaces indent, -nut: no tabs, -st: standard output
        # You can adjust flags as needed. Using simple defaults for now: -st
        cmd = ["wsl", "indent", "-st", "-kr", "-i4", "-nut"]
        
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate(input=code)
        
        if process.returncode != 0:

            return code 
            
        return stdout.strip()
        
    except Exception as e:
        print(f"[WARN] formatting exception: {e}")
        return code

def extract_code_slice(file_path, line_numbers):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            
        # Line numbers are 1-indexed in Joern, 0-indexed in Python
        gadget_lines = []
        for ln in line_numbers:
            if 1 <= ln <= len(all_lines):
                gadget_lines.append(all_lines[ln-1].strip())
        
        return "\n".join(gadget_lines)
    except Exception as e:
        print(f"[!] Error reading file: {e}")
        return ""
