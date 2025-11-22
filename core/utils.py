import os

def clean_filename(s: str) -> str:
    s = s.replace(" ", "_")
    return "".join(c for c in s if c.isalnum() or c in "_-")

def get_files_in_folder(folder: str, extensions=(".png", ".jpg", ".jpeg", ".bmp", ".webp")):
    if not folder or not os.path.exists(folder):
        return []
    
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.lower().endswith(extensions):
                # Get path relative to the input folder
                rel_dir = os.path.relpath(root, folder)
                if rel_dir == ".":
                    files.append(filename)
                else:
                    files.append(os.path.join(rel_dir, filename))
    
    return sorted(files)

def get_next_file(current_file: str, folder: str) -> str:
    files = get_files_in_folder(folder)
    if not files:
        return None
    
    current_name = os.path.basename(current_file)
    try:
        idx = files.index(current_name)
    except ValueError:
        idx = -1
    
    next_idx = (idx + 1) % len(files)
    return os.path.join(folder, files[next_idx])
