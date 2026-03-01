"""RSA key generation and management."""

import os
from pathlib import Path
from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class RSAKeyManager:
    """Manages RSA key pair generation, loading, and saving."""

    def __init__(self, key_dir: Path) -> None:
        """Initialize key manager.

        Args:
            key_dir: Directory to store keys
        """
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.key_dir / "private_key.pem"
        self.public_key_path = self.key_dir / "public_key.pem"

    def generate_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """Generate RSA key pair and save to files.

        Args:
            key_size: Size of the key in bits (default: 2048)

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Extract public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Save keys to files
        self.private_key_path.write_bytes(private_pem)
        self.public_key_path.write_bytes(public_pem)

        # Set restrictive permissions on private key (Unix-like systems)
        if os.name != "nt":  # Not Windows
            os.chmod(self.private_key_path, 0o600)

        return private_pem, public_pem

    def load_private_key(self) -> bytes:
        """Load private key from file.

        Returns:
            Private key in PEM format

        Raises:
            FileNotFoundError: If private key file doesn't exist
        """
        if not self.private_key_path.exists():
            raise FileNotFoundError(f"Private key not found at {self.private_key_path}")
        return self.private_key_path.read_bytes()

    def load_public_key(self) -> bytes:
        """Load public key from file.

        Returns:
            Public key in PEM format

        Raises:
            FileNotFoundError: If public key file doesn't exist
        """
        if not self.public_key_path.exists():
            raise FileNotFoundError(f"Public key not found at {self.public_key_path}")
        return self.public_key_path.read_bytes()

    def keys_exist(self) -> bool:
        """Check if both keys exist.

        Returns:
            True if both private and public keys exist
        """
        return self.private_key_path.exists() and self.public_key_path.exists()


def generate_rsa_keypair(key_size: int = 2048) -> Tuple[bytes, bytes]:
    """Generate RSA key pair without saving to files.

    Args:
        key_size: Size of the key in bits (default: 2048)

    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem, public_pem


def load_private_key(key_path: Path) -> bytes:
    """Load private key from file path.

    Args:
        key_path: Path to private key file

    Returns:
        Private key in PEM format

    Raises:
        FileNotFoundError: If key file doesn't exist
    """
    path = Path(key_path)
    if not path.exists():
        raise FileNotFoundError(f"Private key not found at {path}")
    return path.read_bytes()


def load_public_key(key_path: Path) -> bytes:
    """Load public key from file path.

    Args:
        key_path: Path to public key file

    Returns:
        Public key in PEM format

    Raises:
        FileNotFoundError: If key file doesn't exist
    """
    path = Path(key_path)
    if not path.exists():
        raise FileNotFoundError(f"Public key not found at {path}")
    return path.read_bytes()
