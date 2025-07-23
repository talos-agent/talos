import base64
import os
import unittest

from talos.services.key_management import KeyManagement
from talos.skills.cryptography import CryptographySkill


class CryptographyTest(unittest.TestCase):
    def setUp(self):
        self.key_dir = ".test_keys"
        self.km = KeyManagement(key_dir=self.key_dir)
        self.crypto_skill = CryptographySkill(key_management=self.km)

    def tearDown(self):
        if os.path.exists(self.key_dir):
            for f in os.listdir(self.key_dir):
                os.remove(os.path.join(self.key_dir, f))
            os.rmdir(self.key_dir)

    def test_key_generation(self):
        self.km.generate_keys()
        self.assertTrue(os.path.exists(self.km.private_key_path))
        self.assertTrue(os.path.exists(self.km.public_key_path))

    def test_encryption_decryption(self):
        message = "This is a secret message."
        public_key = self.km.get_public_key()

        encrypted = self.crypto_skill.run(data=message, public_key=base64.b64encode(public_key).decode())

        decrypted = self.crypto_skill.run(data=encrypted, decrypt=True)

        self.assertEqual(message, decrypted)


if __name__ == "__main__":
    unittest.main()
