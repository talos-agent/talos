import os

from nacl.public import PrivateKey, PublicKey, SealedBox


class KeyManagement:
    def __init__(self, key_dir: str = ".keys"):
        self.key_dir = key_dir
        self.private_key_path = os.path.join(self.key_dir, "private_key.pem")
        self.public_key_path = os.path.join(self.key_dir, "public_key.pem")
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)

    def generate_keys(self):
        """
        Generates a new Curve25519 key pair and saves them to the key_dir.
        """
        private_key = PrivateKey.generate()
        public_key = private_key.public_key

        with open(self.private_key_path, "wb") as f:
            f.write(private_key.encode())

        with open(self.public_key_path, "wb") as f:
            f.write(public_key.encode())

    def get_public_key(self) -> bytes:
        """
        Returns the public key as bytes.
        """
        if not os.path.exists(self.public_key_path):
            self.generate_keys()
        with open(self.public_key_path, "rb") as f:
            return f.read()

    def get_private_key(self) -> bytes:
        """
        Returns the private key as bytes.
        """
        if not os.path.exists(self.private_key_path):
            self.generate_keys()
        with open(self.private_key_path, "rb") as f:
            return f.read()

    def encrypt(self, data: str, public_key_bytes: bytes) -> bytes:
        """
        Encrypts data using the public key.
        """
        public_key = PublicKey(public_key_bytes)
        sealed_box = SealedBox(public_key)
        return sealed_box.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypts data using the private key.
        """
        private_key = PrivateKey(self.get_private_key())
        unseal_box = SealedBox(private_key)
        return unseal_box.decrypt(encrypted_data).decode()
