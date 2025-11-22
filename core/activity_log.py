class ActivityLog:
    def __init__(self, max_entries=50):
        self.entries = []
        self.max_entries = max_entries

    def add(self, message: str):
        self.entries.insert(0, message)
        if len(self.entries) > self.max_entries:
            self.entries.pop()
    
    def get_entries(self):
        return self.entries
