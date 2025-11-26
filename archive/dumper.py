```python
import os

def load_ignore_patterns(*files):
    """Load patterns from .gitignore and similar files."""
    patterns = []
    for ignore_file in files:
        if os.path.exists(ignore_file):
            with open(ignore_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
    return patterns


def should_ignore(path, patterns):
    """Simple pattern matching - covers 90% of use cases."""
    name = os.path.basename(path)
    
    for pattern in patterns:
        # Exact match
        if name == pattern.rstrip('/'):
            return True
        
        # Wildcard at start: *.log, *.txt
        if pattern.startswith('*') and name.endswith(pattern[1:]):
            return True
        
        # Wildcard at end: log*, test*
        if pattern.endswith('*') and name.startswith(pattern[:-1]):
            return True
        
        # Directory pattern: node_modules/, build/
        if pattern.endswith('/') and name == pattern[:-1]:
            return True
        
        # Contains pattern: *cache*, *tmp*
        if pattern.startswith('*') and pattern.endswith('*'):
            if pattern[1:-1] in name:
                return True
    
    return False


def dump_project(root_dir=".", output_file="project_dump.txt"):
    # Load ignore patterns
    gitignore = os.path.join(root_dir, ".gitignore")
    gcloudignore = os.path.join(root_dir, ".gcloudignore")
    patterns = load_ignore_patterns(gitignore, gcloudignore)
    
    # Hard-coded excludes that are always skipped
    always_skip = {
        '.git', '__pycache__', '.venv', 'venv', 'node_modules',
        '.expo', 'build', 'dist', '.next', '.cache'
    }
    
    with open(output_file, "w", encoding="utf-8", errors="ignore") as out:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip directories IN-PLACE so os.walk doesn't enter them
            dirnames[:] = [
                d for d in dirnames 
                if d not in always_skip and not should_ignore(d, patterns)
            ]
            
            rel_path = os.path.relpath(dirpath, root_dir)
            if rel_path == ".":
                rel_path = root_dir
            
            out.write(f"\n📂 {rel_path}\n")
            out.write("-" * 40 + "\n")
            
            for filename in filenames:
                # Skip the dumper script and output file
                if filename in {'dumper.py', output_file}:
                    continue
                
                # Skip ignored files
                if should_ignore(filename, patterns):
                    continue
                
                file_path = os.path.join(dirpath, filename)
                rel_file = os.path.relpath(file_path, root_dir)
                
                out.write(f"\n--- {rel_file} ---\n")
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"[Could not read: {e}]\n")
    
    print(f"✅ Done: {output_file}")


if __name__ == "__main__":
    dump_project()

```
