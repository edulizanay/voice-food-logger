import json
import os
from datetime import datetime

def store_food_data(food_items: list, timestamp: datetime = None) -> bool:
    """
    Store food logging entry to daily JSON file
    
    Args:
        food_items: List of food items with 'food' and 'quantity' keys
        timestamp: When the food was consumed (defaults to now)
        
    Returns:
        True if stored successfully
        
    Raises:
        Exception: If storage fails
    """
    if not food_items:
        raise ValueError("food_items cannot be empty")
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Create entry
    entry = {
        "timestamp": timestamp.isoformat(),
        "items": food_items
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get daily log file path
    filename = f"logs_{timestamp.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    # Load existing entries or create new list
    entries = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
            entries = data if isinstance(data, list) else [data]
    
    # Add new entry
    entries.append(entry)
    
    # Save updated entries
    with open(filepath, 'w') as file:
        json.dump(entries, file, indent=2)
    
    print(f"Stored food entry with {len(food_items)} items to {filepath}")
    return True

def get_today_entries() -> list:
    """Get all food entries for today"""
    today = datetime.now()
    filename = f"logs_{today.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join('logs', filename)
    
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r') as file:
        data = json.load(file)
        return data if isinstance(data, list) else [data]

if __name__ == "__main__":
    # Test the storage system
    test_items = [
        {"food": "chicken breast", "quantity": "150 grams"},
        {"food": "rice", "quantity": "0.5 cup"}
    ]
    
    try:
        store_food_data(test_items)
        entries = get_today_entries()
        print(f"Retrieved {len(entries)} entries for today")
        for entry in entries:
            print(f"  {entry['timestamp']}: {len(entry['items'])} items")
    except Exception as e:
        print(f"Error: {e}")