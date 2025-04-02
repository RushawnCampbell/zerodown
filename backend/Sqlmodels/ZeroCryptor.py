from cryptography.fernet import Fernet,InvalidToken, InvalidSignature
import os, hashlib, keyring, getpass

class ZeroCryptor:

    def __init__(self):
        pass
     
    def _generate_key(self, type):
        if self._get_key(type) is None:
            key = Fernet.generate_key()
            key_str = key.decode()
            windows_user = self.get_windows_username()
            self.store_crypto_key(windows_user, key_str, type)

    def store_crypto_key(self,windows_user, key_str ,type):
        try:
            service_name = f"Z_{type}_KEY"
            username = windows_user
            keyring.set_password(service_name, username, key_str)
        except Exception as e:
            err_msg = str(e)
            print("Token Storage Failed", f"Error storing token: {err_msg}")
    

    def _get_key(self, type):
        service_name = f"Z_{type}_KEY"
        username = self.get_windows_username()
        try:
            key = keyring.get_password(service_name, username)
            if not key:
                return None
            return Fernet(key.encode())
        except Exception as e:
            err_msg = str(e)
            print("Token Retrieval Failed", f"Error retrieving token: {err_msg}")
            return None  
    

    def _encrypt_data(self,data, type):
        key = self._get_key(type)
        return key.encrypt(data.encode())
    
    
    def _decrypt_data(self,encrypted_data, type):
        try:
            key = self._get_key(type)
            return key.decrypt(encrypted_data).decode()
        except InvalidToken:
            print(f"Decryption failed: Invalid token")
            return None  # Or raise an exception
        except InvalidSignature:
            print(f"Decryption failed: Invalid signature")
            return None
        except TypeError as e:
            print(f"Decryption failed: Type error - {e}")
            return None
        except Exception as e:
            print(f"Decryption failed: Unexpected error - {e} ")
            return None
    
    
    def _hash_data(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
   
    def _verify_hash(self, hash, data):
        return hash == self.hash_data(data)
    
  
    def get_windows_username(self):
        try:
            username = os.getlogin()
            return username
        except OSError:
            try:
                username = getpass.getuser()
                return username
            except Exception as e:
                print(f"Error getting username: {e}")
                return None
    




""" AES ALTERNATIVE FOR LATER
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac
import os, hashlib, keyring, getpass
import base64

class ZeroCryptor:

    def __init__(self):
        pass

    def _generate_key(self, type):
        if self._get_key(type) is None:
            key = os.urandom(32)  # 256-bit key
            iv = os.urandom(16)   # 128-bit IV
            key_iv = base64.urlsafe_b64encode(key + iv).decode()
            windows_user = self.get_windows_username()
            self.store_crypto_key(windows_user, key_iv, type)

    def store_crypto_key(self, windows_user, key_iv, type):
        try:
            service_name = f"Z_{type}_KEY"
            username = windows_user
            keyring.set_password(service_name, username, key_iv)
        except Exception as e:
            err_msg = str(e)
            print("Token Storage Failed", f"Error storing token: {err_msg}")

    def _get_key(self, type):
        service_name = f"Z_{type}_KEY"
        username = self.get_windows_username()
        try:
            key_iv_b64 = keyring.get_password(service_name, username)
            if not key_iv_b64:
                return None, None
            key_iv = base64.urlsafe_b64decode(key_iv_b64.encode())
            key = key_iv[:32]
            iv = key_iv[32:]
            return key, iv
        except Exception as e:
            err_msg = str(e)
            print("Token Retrieval Failed", f"Error retrieving token: {err_msg}")
            return None, None

    def _encrypt_data(self, data, type):
        key, iv = self._get_key(type)
        if not key or not iv:
            return None
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return base64.urlsafe_b64encode(ciphertext).decode()

    def _decrypt_data(self, encrypted_data, type):
        try:
            key, iv = self._get_key(type)
            if not key or not iv:
                return None
            ciphertext = base64.urlsafe_b64decode(encrypted_data.encode())
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            return data.decode()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    def _hash_data(self, data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _verify_hash(self, hash_value, data):
        return hash_value == self._hash_data(data)

    def get_windows_username(self):
        try:
            username = os.getlogin()
            return username
        except OSError:
            try:
                username = getpass.getuser()
                return username
            except Exception as e:
                print(f"Error getting username: {e}")
                return None"""