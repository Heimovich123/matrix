import os
import json
import unittest
from register_api import load_licenses, save_licenses, LICENSES_FILE

class TestLicenseLogic(unittest.TestCase):
    def setUp(self):
        # Сохраняем оригинальный файл лицензий, если он существует
        self.backup_content = None
        if os.path.exists(LICENSES_FILE):
            with open(LICENSES_FILE, "r", encoding="utf-8") as f:
                self.backup_content = f.read()
                
        # Создаем тестовую базу лицензий
        self.test_data = {
            "keys": {
                "TEST-ACTIVE-1": {
                    "owner": "test1",
                    "max_agents": 1,
                    "registered_agents": [],
                    "active": True
                },
                "TEST-ACTIVE-2": {
                    "owner": "test2",
                    "max_agents": 2,
                    "registered_agents": ["@agent1:server.org"],
                    "active": True
                },
                "TEST-INACTIVE": {
                    "owner": "test3",
                    "max_agents": 1,
                    "registered_agents": [],
                    "active": False
                }
            }
        }
        with open(LICENSES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f, indent=4)

    def tearDown(self):
        # Восстанавливаем оригинальный файл
        if self.backup_content is not None:
            with open(LICENSES_FILE, "w", encoding="utf-8") as f:
                f.write(self.backup_content)
        elif os.path.exists(LICENSES_FILE):
            os.remove(LICENSES_FILE)

    def test_load_licenses(self):
        data = load_licenses()
        self.assertIn("TEST-ACTIVE-1", data["keys"])
        self.assertEqual(data["keys"]["TEST-ACTIVE-1"]["owner"], "test1")

    def test_validate_keys(self):
        licenses = load_licenses()
        keys = licenses.get("keys", {})
        
        # 1. Invalid key
        self.assertNotIn("NON-EXISTENT", keys)
        
        # 2. Inactive key
        key_inactive = keys["TEST-INACTIVE"]
        self.assertFalse(key_inactive.get("active", False))
        
        # 3. Valid key with quota
        key_valid = keys["TEST-ACTIVE-1"]
        self.assertTrue(key_valid.get("active", False))
        self.assertLess(len(key_valid.get("registered_agents", [])), key_valid.get("max_agents", 1))
        
        # 4. Key with reached quota
        key_full = keys["TEST-ACTIVE-2"]
        # Добавим еще одного, чтобы забить квоту
        key_full["registered_agents"].append("@agent2:server.org")
        self.assertEqual(len(key_full["registered_agents"]), key_full["max_agents"])

if __name__ == "__main__":
    unittest.main()
