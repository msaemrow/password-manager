# Password Manager Console App

## Description

A command-line password manager that stores and retrieves passwords. App utilizes Textualize to create a user friendly interface for users.

##

- Add new account name, username, and password
- Retrieve username and password by account name
- Get a list of accounts that have credentials associated with them
- Password required to access the application

## Security

- Upon initial deployment, user is prompted to create a password that is stored and encrypted via fernet key.
- Account information is stored in a JSON file in the app and the passwords are encrypted via a fernet key.

## Installation

1. Clone the repository to local machine
   ```sh
   git clone https://github.com/yourusername/password-manager.git
   ```
2. Navigate into the directory
3. Create a virtual environment
4. Install requirements
5. Run application
6. Follow on screen prompts
