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
    