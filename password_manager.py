from cryptography.fernet import Fernet
import os
import json
from colorama import Fore, Style, Back
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Input, Static
from textual.screen import Screen

def generate_key():
    """
    Generate a key for encryption and save it to a file.
    """
    key=Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print(Fore.GREEN + "Key generated and saved." + Style.RESET_ALL)

def load_key():
    """
    Loads key from secret.key file
    """

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

def add_password(key, service, username, password):
    """
    Prompt user for a service, username and password
    Encrypt and add new password entry to the passwords.json file.
    """
    encrypted_password = encrypt_password(password, key)

    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            try:
                passwords = json.load(file)
            except json.JSONDecodeError:
                passwords = {}
    else:
        passwords = {}
    
    passwords[service] = {
        "username": username,
        "password": encrypted_password.decode()
    }

    with open("passwords.json", "w") as file:
        json.dump(passwords, file, indent=4)
    
    print(Fore.GREEN + f"Successfully added username and password for {service}" + Style.RESET_ALL)

def get_password(key):
    """
    Retrieves username and password from file for a given service and decodes to user
    """
    service = input(Fore.WHITE + "Enter service name: " + Style.RESET_ALL).strip()

    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            try: 
                passwords = json.load(file)
            except json.JSONDecodeError:
                print(Fore.RED + "Error: Password file is corrupt." + Style.RESET_ALL)
                return
            
        if service in passwords:
            username= passwords[service]["username"]
            encrypted_password=  passwords[service]["password"].encode()
            password=decrypt_password(encrypted_password, key)
            print(Fore.CYAN + f"Service: {service}\nUsername: {username}\nPassword: {password}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"No username/password found for {service}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "No passwords found in file" + Style.RESET_ALL)

def main():
    """
    Main function to run the password manager CLI
    """
    if not os.path.exists("secret.key"):
        print(Fore.YELLOW + "Key not found, generating a new key..." + Style.RESET_ALL)
        generate_key() 


    key = load_key()

    while True:
        print(Style.BRIGHT + Fore.CYAN + "\n Password Manager Menu" + Style.RESET_ALL )
        print(Fore.WHITE + "1. Add a new password" + Style.RESET_ALL)
        print(Fore.WHITE + "2. Look up stored password" + Style.RESET_ALL)
        print(Fore.WHITE + "3. Exit" + Style.RESET_ALL)

        choice = input(Style.BRIGHT + Fore.GREEN + "Choose an option (1, 2, or 3)\n" + Style.RESET_ALL).strip()

        if choice == "1":
            add_password(key)
        elif choice == "2":
            get_password(key)
        elif choice == "3":
            print("Exiting Password Manager")
            break
        else:
            print("Invalid option. Enter 1, 2, or 3 to choose an option.")

class PasswordManagerApp(App):
    CSS_PATH = "password.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="plus_sign",
            action="on_button_press",
            description="Add Password",
            key_display="+",
        ),
    ]

    def compose(self):
        yield Vertical(
            Header("Password Manager", classes="header"),
            Button("Add a Password", id="add_password", classes="button", variant="primary"),
            Button("Get Password", id="get_password",classes="button", variant="primary"),
            Button("Exit", id="exit", classes="button", variant="error"),
        )
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handles button click events."""
            key = load_key()

            if event.button.id == "add_password":
                await self.push_screen(AddPasswordScreen(key))
                print("Add Password button clicked!")
            elif event.button.id == "get_password":
                print("Get Password button clicked!")
            elif event.button.id == "exit":
                print("Exiting...")
                self.exit()

    async def action_on_button_press(self, message):
        """Handles button presses"""
        if message.button.id == "add_password":
            await self.push_screen(AddPasswordScreen(self.key))
        elif message.button.id == "get_password":
            await self.push_screen(GetPasswordScreen(self.key))

        elif message.button.id == "exit":
            await self._shutdown()

class AddPasswordScreen(Screen):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def compose(self):
        yield Horizontal(
            VerticalScroll(
                Header("Add new password", classes="header"),
                Input(placeholder="Service", id="add_service", classes="pw_input"),
                Input(placeholder="Username", id="add_username",classes="pw_input"),
                Input(placeholder="Password", id="add_password", classes="pw_input"),
                Input(placeholder="Confirm Password", id="confirm_password", classes="pw_input"),
            ),
            Vertical(
                Button("Add Combination", id="submit", variant="success", classes="button" ),
                Button("Main Menu", id="exit", variant="success", classes="button" )
            )

        )

        yield Footer()

    
    async def on_button_click(self, event: Button.Pressed) -> None:
        """Handles submission button click"""
        self.log(f"Button Pressed: {event.button.id}")

        if event.button.id == "submit":
            service = self.query_one("#add_service", Input).value.strip()
            username = self.query_one("#add_username", Input).value.strip()
            password = self.query_one("#add_password", Input).value.strip()
            confirm_password = self.query_one("#confirmpassword", Input).value.strip()


            if service and username and password and confirm_password:    
                if password == confirm_password:
                    await add_password(self.key, service, username, password)
                    await self.app.pop_screen()
                else:
                    self.log("Passwords must match")
            else:
                self.log("All fields required")
        elif event.button.id == "exit":
                self.log("Returning to main menu...")
                try:
                    await self.app.pop_screen()
                    self.log("Screen popped successfully!")
                except Exception as e:
                    self.log(f"Error popping screen: {e}")

class PasswordScreen(App):
    def __init__(self, key):
        super().__init__()
        self.key = key

    async def on_mount(self):
        self.service_input = Input(placeholder="Enter Service Name", id="service_name")
        self.submit_button = Button("Submit", id="submit")

        await self.view.dock(self.service_input, self.submit_button)

    async def on_button_pressed(self, message):
        """Handles form submission."""
        if message.button.id == "submit":
            service = self.service_input.value.strip()
            if service:
                result = get_password(service, self.key)
                if result:
                    username, password = result
                    print(f"Service: {service}\nUsername: {username}\nPassword: {password}")
                    await self.push_screen(PasswordManagerApp)
                else:
                    print(f"No password found for {service}")
            else:
                print("Service name is required!")
class GetPasswordScreen(App):
    def __init__(self, key):
        super().__init__()
        self.key = key

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.run()