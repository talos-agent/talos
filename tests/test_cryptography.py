import os
import unittest

import nacl.public

from talos.services.key_management import KeyManagement


class CryptographyTest(unittest.TestCase):
    def setUp(self):
        self.key_dir = ".test_keys"
        self.km = KeyManagement(key_dir=self.key_dir)

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

        # Delegate side: encrypt the message with the public key
        public_key = nacl.public.PublicKey(self.km.get_public_key())
        sealed_box = nacl.public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(message.encode())

        # Talos side: decrypt the message with the private key
        decrypted = self.km.decrypt(encrypted)

        self.assertEqual(message, decrypted)


if __name__ == "__main__":
    unittest.main()
