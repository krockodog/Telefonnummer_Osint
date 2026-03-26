"""
Encryption utilities for secure API key storage
Uses XOR encryption with Base64 encoding for obfuscation
"""
import base64
import os
from typing import Optional


class SecureStorage:
    """Simple encryption for API keys - prevents casual exposure"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize with a master key.
        If no key provided, uses SECRET_KEY from environment.
        """
        self.master_key = master_key or os.getenv('SECRET_KEY', 'default-key-change-in-production')
        # Create a deterministic key from master_key
        self._key = self._derive_key(self.master_key)
    
    def _derive_key(self, master_key: str) -> bytes:
        """Derive encryption key from master key"""
        # Simple key derivation - XOR all bytes together and expand
        key_bytes = master_key.encode('utf-8')
        derived = bytearray(32)
        for i, b in enumerate(key_bytes):
            derived[i % 32] ^= b
        return bytes(derived)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string and return base64-encoded result.
        Returns empty string if input is empty.
        """
        if not plaintext:
            return ""
        
        try:
            # Convert to bytes
            data = plaintext.encode('utf-8')
            
            # XOR with key (repeating key)
            encrypted = bytearray()
            for i, b in enumerate(data):
                key_byte = self._key[i % len(self._key)]
                # Add some variation based on position
                variant = (i * 7 + 13) % 256
                encrypted.append(b ^ key_byte ^ variant)
            
            # Add checksum (simple sum of original bytes)
            checksum = sum(data) % 256
            encrypted.append(checksum)
            
            # Base64 encode
            return base64.urlsafe_b64encode(bytes(encrypted)).decode('ascii')
            
        except Exception:
            return ""
    
    def decrypt(self, ciphertext: str) -> Optional[str]:
        """
        Decrypt a base64-encoded encrypted string.
        Returns None if decryption fails.
        """
        if not ciphertext:
            return None
        
        try:
            # Base64 decode
            encrypted = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
            
            if len(encrypted) < 1:
                return None
            
            # Extract checksum (last byte)
            stored_checksum = encrypted[-1]
            encrypted = encrypted[:-1]
            
            # XOR decrypt
            decrypted = bytearray()
            for i, b in enumerate(encrypted):
                key_byte = self._key[i % len(self._key)]
                variant = (i * 7 + 13) % 256
                decrypted.append(b ^ key_byte ^ variant)
            
            # Verify checksum
            calculated_checksum = sum(decrypted) % 256
            if calculated_checksum != stored_checksum:
                # Checksum mismatch - might be unencrypted data
                # Try returning as-is (for backward compatibility)
                try:
                    return ciphertext
                except:
                    return None
            
            return decrypted.decode('utf-8')
            
        except Exception:
            # If decryption fails, assume it's unencrypted
            return ciphertext
    
    def encrypt_env_value(self, value: str) -> str:
        """Encrypt a value for storage in .env file"""
        encrypted = self.encrypt(value)
        return f"ENC:{encrypted}"
    
    def decrypt_env_value(self, value: str) -> Optional[str]:
        """Decrypt a value from .env file"""
        if value and value.startswith("ENC:"):
            encrypted = value[4:]  # Remove ENC: prefix
            return self.decrypt(encrypted)
        return value


# Global secure storage instance
_secure_storage: Optional[SecureStorage] = None


def get_secure_storage() -> SecureStorage:
    """Get or create global secure storage instance"""
    global _secure_storage
    if _secure_storage is None:
        _secure_storage = SecureStorage()
    return _secure_storage


def encrypt_key(plaintext: str) -> str:
    """Encrypt an API key for storage"""
    return get_secure_storage().encrypt_env_value(plaintext)


def decrypt_key(ciphertext: str) -> Optional[str]:
    """Decrypt an API key from storage"""
    return get_secure_storage().decrypt_env_value(ciphertext)


# CLI for encrypting keys
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python crypto_utils.py <api_key_to_encrypt>")
        print("\nExample:")
        print('  python crypto_utils.py "sk-your-api-key"')
        sys.exit(1)
    
    key_to_encrypt = sys.argv[1]
    encrypted = encrypt_key(key_to_encrypt)
    print(f"\nOriginal: {key_to_encrypt}")
    print(f"Encrypted: {encrypted}")
    print("\nAdd this to your .env file:")
    print(f"  KIMI_API_KEY={encrypted}")
