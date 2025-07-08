import os
import json
from pathlib import Path
from datetime import datetime

class DataManager:
    """Manages data directory creation and file operations for psychological tests"""
    
    def __init__(self):
        self.data_dir = self._get_data_directory()
    
    def _get_data_directory(self):
        """Get appropriate data directory for the platform"""
        if os.name == 'posix':  # macOS/Linux
            return Path.home() / "orexin_data"
        else:  # Windows
            return Path.home() / "AppData" / "Local" / "Vigila"
    
    def check_data_setup(self):
        """Check if data directory can be created and files can be written"""
        # Try to create data directory
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return f"Error: Cannot create data directory '{self.data_dir}': {e}"
        
        # Try to create a test file to verify write permissions
        test_file = self.data_dir / "test_write.tmp"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()
        except OSError as e:
            return f"Error: Cannot write to data directory '{self.data_dir}': {e}"
        
        return None
    
    def save_test_data(self, test_name, data):
        """Save test data to JSON file, appending to existing data"""
        filename = f"{test_name}.json"
        filepath = self.data_dir / filename
        
        # Add timestamp to the data
        data_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **data
        }
        
        try:
            # Read existing data if file exists
            existing_data = []
            if filepath.exists():
                with open(filepath, 'r') as f:
                    existing_data = json.load(f)
            
            # Append new data
            existing_data.append(data_with_timestamp)
            
            # Write back to file
            with open(filepath, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return str(filepath)
        except OSError as e:
            raise OSError(f"Error saving data to '{filepath}': {e}")
        except json.JSONDecodeError as e:
            raise OSError(f"Error reading existing data from '{filepath}': {e}")
    
    def get_data_directory_path(self):
        """Get the data directory path as string"""
        return str(self.data_dir)