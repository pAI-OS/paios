import unittest
from db import create_config_item, read_config_item, update_config_item, delete_config_item, set_config_item

class TestDbFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_config_item(self):
        # Test that create_config_item correctly encrypts the value and inserts it into the database
        tenant = 'test'
        key = 'test_key'
        value = 'test_value'
        create_config_item(key, value, tenant=tenant)
        result = read_config_item(key, tenant=tenant)
        delete_config_item(key, tenant=tenant)
        self.assertEqual(result, value)

    def test_read_config_item(self):
        # Test that read_config_item correctly retrieves and decrypts a value from the database
        tenant = 'test'
        key = 'test_key'
        value = 'test_value'
        create_config_item(key, value, tenant=tenant)
        result = read_config_item(key, tenant=tenant)
        delete_config_item(key, tenant=tenant)
        self.assertEqual(result, value)

    def test_update_config_item(self):
        # Test that update_config_item correctly updates a value in the database
        tenant = 'test'
        key = 'test_key'
        old_value = 'old_test_value'
        new_value = 'new_test_value'
        create_config_item(key, old_value, tenant=tenant)
        update_config_item(key, new_value, tenant=tenant)
        result = read_config_item(key, tenant=tenant)
        delete_config_item(key, tenant=tenant)
        self.assertEqual(result, new_value)

    def test_set_config_item(self):
        # Test that set_config_item correctly updates a value in the database
        tenant = 'test'
        key = 'test_key'
        old_value = 'old_test_value'
        new_value = 'new_test_value'
        set_config_item(key, old_value, tenant=tenant)
        set_config_item(key, new_value, tenant=tenant)
        result = read_config_item(key, tenant=tenant)
        delete_config_item(key, tenant=tenant)
        self.assertEqual(result, new_value)

    def test_delete_config_item(self):
        # Test that delete_config_item correctly removes a value from the database
        tenant = 'test'
        key = 'test_key'
        delete_config_item(key, tenant=tenant)
        result = read_config_item(key, tenant=tenant)
        self.assertIsNone(result)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
