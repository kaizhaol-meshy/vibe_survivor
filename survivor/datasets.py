import json
import os

class Dataset:
    def __init__(self, data):
        self.data = data
    
    @classmethod
    def from_list(cls, data_list):
        return cls(data_list)
    
    def save_to_disk(self, path):
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(path, 'w') as f:
            json.dump(self.data, f)
        
        print(f"Saved dataset to {path}")
        return self 