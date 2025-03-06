import json
import os
from encryption import encrypt_password, decrypt_password

STORAGE_FILE = "passwords.json"

def load_passwords():
    """Loads passwords from JSON file"""
    if not os.path.exists(STORAGE_FILE):
        print("No password file found")
        return {}
    
    with open(STORAGE_FILE, "r") as file:
        print("Loading passwords from file...")
        return json.load(file)
    
def save_password(passwords):
    """Saves service, username, and password to JSON file"""
    with open(STORAGE_FILE, "w") as file:
        print("saving password...")
        json.dump(passwords, file, indent=4)

def add_password(key, account, username, password):
    """
    Prompt user for a service, username and password
    Encrypt and add new password entry to the passwords.json file.
    """

    passwords=load_passwords()
    passwords[account] = {
        "username": username,
        "password": encrypt_password(password, key).decode(),
        }    
    save_password(passwords)
    
def get_password(account, key):
    """Retrieves and decrypts a stored password"""
    passwords = load_passwords()

    if account not in passwords:
        print(f"account {account} not found in stored passwords")
        return None
    
    try:
        account_info = passwords[account]
        username = account_info["username"]
        encrypted_password = account_info["password"]
        decrypted_password = decrypt_password(encrypted_password, key)
        return {"account": account, "username": username, "password": decrypted_password}
    except Exception as e:
        print(f"Error in get_password function: {e}")
        return None
    
def get_account_list():
    """Retrieves list of all account names. No username or password information"""
    passwords = load_passwords()
    return passwords.keys()

def add_login_pw(key, password):
    """
    Prompt user for a service, username and password
    Encrypt and add new password entry to the passwords.json file.
    """

    passwords=load_passwords()
    passwords['login_pw'] = {
        "username": "default_user",
        "password": encrypt_password(password, key).decode(),
        }    
    save_password(passwords)

def get_login_pw(key):
    """Retrieves list of all account names. No username or password information"""
    passwords = load_passwords()
    encrypted_password = passwords['login_pw']['password']
    decrypted_password = decrypt_password(encrypted_password, key)
    return decrypted_password