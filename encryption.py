from cryptography.fernet import Fernet
import os

def generate_key():
    """
    Generate a key for encryption and save it to a file.
    """
    if not os.path.exists("secret.key"):
        key=Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        print("Key generated and saved.")
    else:
        print("Key already exists")

def load_key():
    """
    Loads key from secret.key file
    """
    print("Loading key...")
    return open("secret.key", "rb").read()

def encrypt_password(password, key):
    """
    Encrypts password using key
    """
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password, key):
    """
    Decrypts the encrypted password using key
    """
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password

generate_key()