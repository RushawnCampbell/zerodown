import os
import paramiko, time

class ZeroEndpoint():

    def __init__(self):
        self.key_path= os.path.join(os.path.expanduser("~"), ".ssh", "zero_endpoint") 
        self.key=''
    
    def keys_generator(self):
       try:
           keys_dir = os.path.dirname(self.key_path)
           if not os.path.exists(keys_dir):
               os.makedirs(keys_dir)
               print(f"Created directory: {keys_dir}")
               time.sleep(5)
               
           if os.path.exists(self.key_path) or os.path.exists(self.key_path + ".pub"):
               print(f"Key pair already exists at {self.key_path}. Skipping generation.")
               time.sleep(5)
               return -1

           self.key = paramiko.RSAKey.generate(4096) 

           # Saving private key
           self.key.write_private_key_file(self.key_path)
           print(f"Private key saved to {self.key_path}")

           # Saving public key
           pub_key = self.key.get_name() + " " + self.key.get_base64()
           with open(self.key_path + ".pub", "w") as f:
               f.write(pub_key)
           print(f"Public key saved to {self.key_path}.pub")
           time.sleep(15)

       except Exception as e:
           print(f"Error generating keys: {e}")
           time.sleep(15)


if __name__ == "__main__":
    zeroendpoint = ZeroEndpoint()
    zeroendpoint.keys_generator()



