import unittest
from backend.managers.ConfigManager import ConfigManager
import asyncio

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.config_manager = ConfigManager()

    def asyncTest(func):
        def wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        return wrapper

    @asyncTest
    async def test_create_config_item(self):
        value = 'test_value'
        key = await self.config_manager.create_config_item(value)
        result = await self.config_manager.retrieve_config_item(key)
        await self.config_manager.delete_config_item(key)
        self.assertEqual(result, value)

    @asyncTest
    async def test_read_config_item(self):
        value = 'test_value'
        key = await self.config_manager.create_config_item(value)
        result = await self.config_manager.retrieve_config_item(key)
        await self.config_manager.delete_config_item(key)
        self.assertEqual(result, value)

    @asyncTest
    async def test_update_config_item(self):
        value = 'test_value'
        key = await self.config_manager.create_config_item(value)
        new_value = 'new_test_value'
        await self.config_manager.update_config_item(key, new_value)
        result = await self.config_manager.retrieve_config_item(key)
        await self.config_manager.delete_config_item(key)
        self.assertEqual(result, new_value)

    @asyncTest
    async def test_delete_config_item(self):
        value = 'test_value'
        key = await self.config_manager.create_config_item(value)
        await self.config_manager.delete_config_item(key)
        result = await self.config_manager.retrieve_config_item(key)
        self.assertIsNone(result)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
