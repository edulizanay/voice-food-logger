import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json
import tempfile
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import FoodStorage, store_food_data, get_today_entries

class TestFoodStorage(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FoodStorage(self.temp_dir)
        self.test_items = [
            {"food": "chicken breast", "quantity": "150 grams"},
            {"food": "brown rice", "quantity": "0.5 cup"}
        ]
        self.test_timestamp = datetime(2024, 1, 15, 10, 30, 0)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directory(self):
        """Test that initialization creates the logs directory"""
        new_temp_dir = os.path.join(self.temp_dir, "new_logs")
        storage = FoodStorage(new_temp_dir)
        
        self.assertTrue(os.path.exists(new_temp_dir))
    
    def test_get_daily_log_path(self):
        """Test daily log file path generation"""
        path = self.storage._get_daily_log_path(self.test_timestamp)
        expected = os.path.join(self.temp_dir, "logs_2024-01-15.json")
        
        self.assertEqual(path, expected)
    
    def test_store_food_entry_success(self):
        """Test successful food entry storage"""
        success = self.storage.store_food_entry(self.test_items, self.test_timestamp)
        
        self.assertTrue(success)
        
        # Verify file was created and contains correct data
        log_path = self.storage._get_daily_log_path(self.test_timestamp)
        self.assertTrue(os.path.exists(log_path))
        
        with open(log_path, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['timestamp'], self.test_timestamp.isoformat())
        self.assertEqual(data[0]['items'], self.test_items)
    
    def test_store_multiple_entries_same_day(self):
        """Test storing multiple entries on the same day"""
        # Store first entry
        success1 = self.storage.store_food_entry(self.test_items, self.test_timestamp)
        self.assertTrue(success1)
        
        # Store second entry
        second_items = [{"food": "apple", "quantity": "1 piece"}]
        second_timestamp = datetime(2024, 1, 15, 14, 30, 0)
        success2 = self.storage.store_food_entry(second_items, second_timestamp)
        self.assertTrue(success2)
        
        # Verify both entries exist
        entries = self.storage.get_daily_entries(self.test_timestamp)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['items'], self.test_items)
        self.assertEqual(entries[1]['items'], second_items)
    
    def test_store_food_entry_invalid_input(self):
        """Test storage with invalid input"""
        # Empty items
        success = self.storage.store_food_entry([], self.test_timestamp)
        self.assertFalse(success)
        
        # Non-list items
        success = self.storage.store_food_entry("not a list", self.test_timestamp)
        self.assertFalse(success)
        
        # Invalid item structure
        invalid_items = [{"name": "chicken"}]  # Missing 'food' and 'quantity' keys
        success = self.storage.store_food_entry(invalid_items, self.test_timestamp)
        self.assertFalse(success)
    
    def test_load_daily_log_empty(self):
        """Test loading from non-existent log file"""
        entries = self.storage._load_daily_log(self.test_timestamp)
        self.assertEqual(entries, [])
    
    def test_load_daily_log_legacy_format(self):
        """Test loading old single-entry format"""
        log_path = self.storage._get_daily_log_path(self.test_timestamp)
        
        # Create legacy format file (single object instead of array)
        legacy_data = {
            "timestamp": self.test_timestamp.isoformat(),
            "items": self.test_items
        }
        
        with open(log_path, 'w') as f:
            json.dump(legacy_data, f)
        
        entries = self.storage._load_daily_log(self.test_timestamp)
        
        self.assertIsInstance(entries, list)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], legacy_data)
    
    def test_load_daily_log_corrupted(self):
        """Test loading corrupted log file"""
        log_path = self.storage._get_daily_log_path(self.test_timestamp)
        
        # Create corrupted JSON file
        with open(log_path, 'w') as f:
            f.write("invalid json content")
        
        entries = self.storage._load_daily_log(self.test_timestamp)
        self.assertEqual(entries, [])
    
    def test_get_daily_entries(self):
        """Test retrieving entries for a specific day"""
        # Store some entries
        self.storage.store_food_entry(self.test_items, self.test_timestamp)
        
        # Retrieve entries
        entries = self.storage.get_daily_entries(self.test_timestamp)
        
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['items'], self.test_items)
    
    def test_get_daily_entries_default_today(self):
        """Test retrieving today's entries when no date specified"""
        today = datetime.now()
        self.storage.store_food_entry(self.test_items, today)
        
        entries = self.storage.get_daily_entries()
        
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['items'], self.test_items)
    
    @patch('storage.datetime')
    def test_store_food_entry_default_timestamp(self, mock_datetime):
        """Test storing entry with default timestamp"""
        mock_now = datetime(2024, 1, 20, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        success = self.storage.store_food_entry(self.test_items)
        self.assertTrue(success)
        
        entries = self.storage.get_daily_entries(mock_now)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['timestamp'], mock_now.isoformat())
    
    def test_backup_logs(self):
        """Test backup functionality"""
        # Store some data first
        self.storage.store_food_entry(self.test_items, self.test_timestamp)
        
        # Create backup
        backup_path = os.path.join(self.temp_dir, "backup")
        success = self.storage.backup_logs(backup_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup contains the same data
        backup_file = os.path.join(backup_path, "logs_2024-01-15.json")
        self.assertTrue(os.path.exists(backup_file))
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        self.assertEqual(len(backup_data), 1)
        self.assertEqual(backup_data[0]['items'], self.test_items)
    
    def test_backup_logs_no_directory(self):
        """Test backup when logs directory doesn't exist"""
        empty_storage = FoodStorage(os.path.join(self.temp_dir, "nonexistent"))
        os.rmdir(os.path.join(self.temp_dir, "nonexistent"))  # Remove the auto-created directory
        
        backup_path = os.path.join(self.temp_dir, "backup")
        success = empty_storage.backup_logs(backup_path)
        
        self.assertFalse(success)
    
    @patch('storage.FoodStorage')
    def test_convenience_functions(self, mock_storage_class):
        """Test convenience functions"""
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance
        
        # Test store_food_data
        mock_storage_instance.store_food_entry.return_value = True
        result = store_food_data(self.test_items, self.test_timestamp)
        
        self.assertTrue(result)
        mock_storage_instance.store_food_entry.assert_called_once_with(self.test_items, self.test_timestamp)
        
        # Test get_today_entries
        mock_storage_instance.get_daily_entries.return_value = [{"test": "data"}]
        result = get_today_entries()
        
        self.assertEqual(result, [{"test": "data"}])
        mock_storage_instance.get_daily_entries.assert_called_once_with()

if __name__ == '__main__':
    # Add missing import for timedelta used in get_recent_entries
    from datetime import timedelta
    
    # Add the missing import to the storage module for testing
    import storage
    storage.timedelta = timedelta
    
    unittest.main()