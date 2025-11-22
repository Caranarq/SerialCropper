import os
import shutil
from core.utils import get_files_in_folder

class BatchManager:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.todo_dir = os.path.join(root_dir, "_para_procesar")
        self.done_dir = os.path.join(root_dir, "_processed")
        self.output_dir = os.path.join(root_dir, "_output")
        
        # Create directories if they don't exist
        # If root_dir is just a folder with images, we might want to adapt?
        # But for now, we enforce the structure or create it.
        if not os.path.exists(self.todo_dir):
             # If _para_procesar doesn't exist, maybe the root_dir IS the todo dir?
             # Let's assume strict structure for now as per architecture, 
             # but if empty, maybe warn? 
             # Or we can treat root_dir as the source if _para_procesar is missing?
             # Let's stick to creating them to be safe and consistent.
             os.makedirs(self.todo_dir, exist_ok=True)
        
        os.makedirs(self.done_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
            
        self.files = []
        self.current_index = -1

    def scan(self):
        self.files = get_files_in_folder(self.todo_dir)
        # If no files in todo, maybe check root? No, stick to structure.
        self.current_index = 0 if self.files else -1
        return len(self.files)

    def current_path(self):
        if 0 <= self.current_index < len(self.files):
            return os.path.join(self.todo_dir, self.files[self.current_index])
        return None

    def next_image(self):
        if not self.files:
            return None
        
        self.current_index = (self.current_index + 1) % len(self.files)
        return self.current_path()
    
    def prev_image(self):
        if not self.files:
            return None
        self.current_index = (self.current_index - 1) % len(self.files)
        return self.current_path()

    def mark_current_processed(self):
        path = self.current_path()
        if path and os.path.exists(path):
            # Use the relative path stored in self.files to preserve structure
            rel_path = self.files[self.current_index]
            dest = os.path.join(self.done_dir, rel_path)
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            try:
                shutil.move(path, dest)
                # Remove from list
                self.files.pop(self.current_index)
                # Adjust index
                if self.current_index >= len(self.files):
                    self.current_index = 0 if self.files else -1
                return True
            except Exception as e:
                print(f"Error moving file: {e}")
                return False
        return False
