import os
import fnmatch

def load_ignore_patterns(*files):
    """Load ignore patterns from multiple ignore files (like .gitignore, .gcloudignore)."""
    patterns = []
    for ignore_file in files:
        if os.path.exists(ignore_file):
            with open(ignore_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    patterns.append(line)
    return patterns


def is_ignored(path, patterns, root_dir):
    """Check if a file or folder should be ignored based on ignore patterns."""
    rel_path = os.path.relpath(path, root_dir)
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path, os.path.join("*", pattern)):
            return True
    return False


def dump_project(root_dir=".", output_file="project_dump.txt"):
    # Ignore sources
    gitignore_path = os.path.join(root_dir, ".gitignore")
    gcloudignore_path = os.path.join(root_dir, ".gcloudignore")
    ignore_patterns = load_ignore_patterns(gitignore_path, gcloudignore_path)

    # Default directories & files to skip
    exclude_dirs = {'.git', '__pycache__', '.venv', 'node_modules'}
    exclude_files = {'dumper.py', output_file}

    with open(output_file, "w", encoding="utf-8", errors="ignore") as out:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip ignored or excluded directories
            dirnames[:] = [
                d for d in dirnames
                if d not in exclude_dirs and not is_ignored(os.path.join(dirpath, d), ignore_patterns, root_dir)
            ]

            # Write directory info
            rel_path = os.path.relpath(dirpath, root_dir)
            if rel_path == ".":
                rel_path = root_dir
            out.write(f"\n📂 Directory: {rel_path}\n")
            out.write("-" * (len(rel_path) + 12) + "\n")

            for filename in filenames:
                if filename in exclude_files:
                    continue  # skip dumper.py and output file itself

                file_path = os.path.join(dirpath, filename)
                if is_ignored(file_path, ignore_patterns, root_dir):
                    continue  # skip ignored files

                out.write(f"\n--- File: {os.path.relpath(file_path, root_dir)} ---\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"[Error reading file: {e}]\n")

    print(f"✅ Project dump saved to {output_file} (excluding dumper.py, .gitignore, .gcloudignore files, and ignored items)")


if __name__ == "__main__":
    dump_project(root_dir=".", output_file="project_dump.txt")
