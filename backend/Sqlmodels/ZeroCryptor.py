from cryptography.fernet import Fernet
import os, hashlib

class ZeroCryptor:

    def __init__(self):
        pass
     
    @staticmethod
    def _generate_key(type):
        if type == "STORAGE" and os.environ.get('ZEROGUARDIAN_STORAGE'):
            return None
        
        if type == "ENDPOINT" and os.environ.get('ZEROGUARDIAN_ENDPOINT'):
            return None

        key = Fernet.generate_key()
        key_str = key.decode()

        if type == "STORAGE":
            os.environ['ZEROGUARDIAN_STORAGE'] = key_str
            return key_str
        
        if type == "ENDPOINT":
            os.environ['ZEROGUARDIAN_ENDPOINT'] = key_str
            return key_str
        return -1
    
    @staticmethod 
    def _get_key(type):
        key=""
        if type =="STORAGE":
            key = os.environ.get('ZEROGUARDIAN_STORAGE')
        if type == "ENDPOINT":
            key = os.environ.get("ZEROGUARDIAN_ENDPOINT")
        if not key or key == None:
            key = ZeroCryptor._generate_key(type)
            if key == -1:
                raise ValueError(f"Error Generating Key")
        return Fernet(key.encode())

    @staticmethod 
    def _encrypt_data(data, type):
        key = ZeroCryptor._get_key(type)
        return key.encrypt(data.encode())
    
    @staticmethod 
    def _decrypt_data(encrypted_data, type):
        try:
            key = ZeroCryptor._get_key(type)
            return key.decrypt(encrypted_data).decode()
        except Exception as e:
            print("ERROR IS", e)
    
    @staticmethod
    def _hash_data(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _verify_hash(self, hash, data):
        return hash == self.hash_data(data)
