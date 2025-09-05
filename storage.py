import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class FoodStorage:
    def __init__(self, logs_directory: str = "logs"):
        self.logs_directory = logs_directory
        self._ensure_logs_directory()
    
    def _ensure_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)
    
    def _get_daily_log_path(self, date: datetime = None) -> str:
        """Get the file path for today's log file"""
        if date is None:
            date = datetime.now()
        filename = f"logs_{date.strftime('%Y-%m-%d')}.json"
        return os.path.join(self.logs_directory, filename)
    
    def _load_daily_log(self, date: datetime = None) -> List[Dict]:
        """Load existing entries for the specified day"""
        log_path = self._get_daily_log_path(date)
        
        if not os.path.exists(log_path):
            return []
        
        try:
            with open(log_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Handle both old format (single entry) and new format (list of entries)
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
                else:
                    print(f"Warning: Unexpected data format in {log_path}")
                    return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading log file {log_path}: {e}")
            return []
    
    def _save_daily_log(self, entries: List[Dict], date: datetime = None):
        """Save entries to the daily log file"""
        log_path = self._get_daily_log_path(date)
        
        try:
            with open(log_path, 'w', encoding='utf-8') as file:
                json.dump(entries, file, indent=2, ensure_ascii=False)
            print(f"Successfully saved {len(entries)} entries to {log_path}")
        except IOError as e:
            print(f"Error writing to log file {log_path}: {e}")
            raise
    
    def store_food_entry(self, food_items: List[Dict], timestamp: datetime = None) -> bool:
        """
        Store a food logging entry
        
        Args:
            food_items: List of food items with 'food' and 'quantity' keys
            timestamp: When the food was consumed (defaults to now)
            
        Returns:
            True if stored successfully, False otherwise
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if not food_items or not isinstance(food_items, list):
            print("Error: food_items must be a non-empty list")
            return False
        
        # Validate food items structure
        for item in food_items:
            if not isinstance(item, dict) or 'food' not in item or 'quantity' not in item:
                print(f"Error: Invalid food item structure: {item}")
                return False
        
        # Create entry
        entry = {
            "timestamp": timestamp.isoformat(),
            "items": food_items
        }
        
        try:
            # Load existing entries for the day
            existing_entries = self._load_daily_log(timestamp)
            
            # Add new entry
            existing_entries.append(entry)
            
            # Save updated entries
            self._save_daily_log(existing_entries, timestamp)
            
            print(f"Stored food entry with {len(food_items)} items at {timestamp.isoformat()}")
            return True
            
        except Exception as e:
            print(f"Error storing food entry: {e}")
            return False
    
    def get_daily_entries(self, date: datetime = None) -> List[Dict]:
        """Get all food entries for a specific day"""
        return self._load_daily_log(date)
    
    def get_recent_entries(self, days: int = 7) -> Dict[str, List[Dict]]:
        """Get entries from the last N days"""
        result = {}
        current_date = datetime.now()
        
        for i in range(days):
            date = datetime(current_date.year, current_date.month, current_date.day) - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            entries = self._load_daily_log(date)
            if entries:
                result[date_str] = entries
        
        return result
    
    def backup_logs(self, backup_path: str) -> bool:
        """Create a backup of all log files"""
        try:
            import shutil
            if os.path.exists(self.logs_directory):
                shutil.copytree(self.logs_directory, backup_path)
                print(f"Backup created at {backup_path}")
                return True
            else:
                print("No logs directory found to backup")
                return False
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

def store_food_data(food_items: List[Dict], timestamp: datetime = None) -> bool:
    """Convenience function to store food data"""
    storage = FoodStorage()
    return storage.store_food_entry(food_items, timestamp)

def get_today_entries() -> List[Dict]:
    """Convenience function to get today's entries"""
    storage = FoodStorage()
    return storage.get_daily_entries()

if __name__ == "__main__":
    # Test the storage system
    test_items = [
        {"food": "chicken breast", "quantity": "150 grams"},
        {"food": "rice", "quantity": "0.5 cup"}
    ]
    
    # Test storing data
    success = store_food_data(test_items)
    if success:
        print("Test storage successful")
        
        # Test retrieving data
        entries = get_today_entries()
        print(f"Retrieved {len(entries)} entries for today:")
        for entry in entries:
            print(f"  {entry['timestamp']}: {len(entry['items'])} items")
    else:
        print("Test storage failed")