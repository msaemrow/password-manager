from textual.app import App, ComposeResult
from textual.containers import Container,Horizontal, Vertical, Center
from textual.widgets import Footer, Button, Input, Static, Label
from textual import on
from textual.screen import Screen
from storage import add_password, get_password, get_account_list, add_login_pw, get_login_pw, load_passwords
from encryption import load_key

class PasswordPrompt(App):
    """Prompt for password before accessing the main app."""
    BINDINGS = [("esc", "pop_screen", "Close")]
    CSS_PATH = "textual.tcss"  

    def compose(self) -> ComposeResult:
        with Container(id="password_prompt_container"):
            yield Vertical(
                Label("Enter Password", id="password_prompt_label"),
                Input(placeholder="Enter your password", id="password_input", classes="password_prompt_input"),
            )
           
            yield Horizontal(
                Button("Submit", id="submit_password", classes="password_prompt_buttons"),
                Button("Exit App", id="exit_app", classes="password_prompt_buttons"),
            )
            yield Footer()

    @on(Button.Pressed, "#exit_app")
    def action_pop_screen(self):
        return self.app.exit()
    
    @on(Button.Pressed, "#submit_password")
    def verify_password(self):
        key = load_key()
        input_password = self.query_one("#password_input", Input).value.strip()
        password = get_login_pw(key)
        print(f"Password {password}")

        if input_password == password:
            self.push_screen(PasswordManagerHome())
        else:
            self.query_one("#password_prompt_label", Label).update("Incorrect password, try again.")


class AddPassword(Screen):
    CSS_PATH = "textual.tcss"    
    

    BINDINGS = [("esc", "pop_screen", "Close")]
    def compose(self) -> ComposeResult:
        with Container(id="add_password_container"):

            with Vertical(id="input_button_container"):
                self.success_message_container = Label("", id="success_message")
                yield self.success_message_container
                yield Label("Enter Account Name", classes="add_password_label")
                yield Input(placeholder="Add Account Name...", id="account_input", classes="add_password_inputs")
                yield Label("Enter Username", classes="add_password_label")
                yield Input(placeholder="Add Username...", id="username_input", classes="add_password_inputs")
                yield Label("Enter Password", classes="add_password_label")
                yield Input(placeholder="Add Password...", id="password_input", classes="add_password_inputs")
            yield Horizontal(
                Button("Add Password", classes="add_password_buttons", id="add_password_button"),
                Button("Main Menu", classes="add_password_buttons", id="return")
            )


    @on(Button.Pressed, "#add_password_button")
    def add_password(self):
        account_input = self.query_one("#account_input", Input)
        account = account_input.value.strip().lower()
        username_input = self.query_one("#username_input", Input)
        username = username_input.value.strip()
        password_input = self.query_one("#password_input", Input)
        password = password_input.value.strip()

        if not account or not username or not password:
            print(f"Account: '{account}' Username: '{username}' Password: '{password}'")
            self.success_message_container.update(f"All fields are required.")
            return
        
        try:
            key = load_key()
            print(f"Key: {key}")
            add_password(key, account, username, password)
            self.success_message_container.update(f"Successfully added password for {account}.")
            
            account_input.clear()
            username_input.clear()
            password_input.clear()
        except Exception as e:
            print(f"Error: {e}")
            self.success_message_container.update(f"Error adding password for {account}: {e}.")


    @on(Button.Pressed, "#return")
    def exit_app(self):
        print("Exiting...")
        self.app.pop_screen()

class GetPassword(Screen):
    CSS_PATH = "textual.tcss"    
    def compose(self) -> ComposeResult:
        with Container(id="get_container"):
            with Center(id="get_pw_input_container"):
                yield Label("Enter Account Name", id="get_password_label")
                yield Input(placeholder="Enter account name here", id="account_name", classes="get_password_inputs")
            with Vertical(id="account_information_container"):
                self.account_name_label = Label("", id="account_name")
                self.account_user_label = Label("", id="account_user")
                self.account_pw_label = Label("", id="account_pw")
                yield self.account_name_label
                yield self.account_user_label
                yield self.account_pw_label
                
           
            with Horizontal(id="button_container"):
                yield Button("Lookup", id="lookup_password", classes="get_password_buttons")
                yield Button("Main Menu", id="return", classes="get_password_buttons")
            
    @on(Button.Pressed, "#lookup_password")
    def lookup_password(self):
        input = self.query_one("#account_name", Input)
        account = input.value.strip().lower()
        if account:
            try:
                key = load_key()
                try:
                    account_info = get_password(account, key)
                    print(f"account info: {account_info}")
                except Exception as e:
                    self.account_name_label.update("Error fetching account info")
                    print(f"Error fetching account info {e}")
                    return
                if account_info is None:
                    self.account_name_label.update("No account info found")
                    self.account_user_label.update("")
                    self.account_pw_label.update("")
                    print("No account info found")
                    return
                
                try:
                    self.account_name_label.update(f"Account Name: {account_info['account']}")
                    self.account_user_label.update(f"Username: {account_info['username']}")
                    self.account_pw_label.update(f"Password: {account_info['password']}")
                except Exception as e:
                    print(f"Error: {e}")
                    self.account_name_label.update(f"Error updating labels {e}")
            except Exception as e:
                    print(f"Unknown Error: {e}")
                    self.account_name_label.update(f"Unknown error{e}")
        input.clear()

    @on(Button.Pressed, "#return")
    def exit_app(self):
        print("Exiting...")
        self.app.pop_screen()


class ViewAccounts(Screen):
    CSS_PATH = "textual.tcss"    
    def compose(self) -> ComposeResult:
        with Container(id="get_container"):
            with Center(id="get_pw_input_container"):
                yield Label("View All Accounts")
            with Vertical(id="account_information_container"):
                account_names = get_account_list()
                self.account_labels = []
                for account in account_names:
                    safe_account_name = account.replace(" ","_")
                    label = Label(account.title() , id=f"account_{safe_account_name}")    
                    self.account_labels.append(label)  
                    yield label         
           
            with Horizontal(id="button_container"):
                yield Button("Main Menu", id="return", classes="get_password_buttons")


    @on(Button.Pressed, "#return")
    def exit_app(self):
        print("Exiting...")
        self.app.pop_screen()


class PasswordManagerHome(Screen):
    CSS_PATH = "textual.tcss"    

    BINDINGS = [("a", "add_pw", "Add"), ("l", "lookup_pw", "Lookup")]
    def compose(self) -> ComposeResult:
        with Container(id="home_container"):
            yield Label("Welcome to the Password Manager", id="home_title")
        with Vertical(id="button_container"):  
                yield Label("Select an option", id="home_label")
                with Center():
                    yield Button("Add Password", id="add_password", classes="home_buttons")
                    yield Button("Lookup Password", id="get_password", classes="home_buttons")
                    yield Button("View Accounts", id="view_accounts", classes="home_buttons")
                    yield Button("Exit App", id="exit", classes="home_buttons")

        yield Footer()

    def action_add_pw(self) -> None:
        self.app.push_screen(AddPassword())

    def action_lookup_pw(self) -> None:
        self.app.push_screen(GetPassword())
    
    def action_view_accounts(self) -> None:
        self.app.push_screen(ViewAccounts())

    def action_exit_app(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#add_password")
    def add_pw(self) -> None:
        self.app.push_screen(AddPassword())

    @on(Button.Pressed, "#get_password")
    def get_pw(self) -> None:
        self.app.push_screen(GetPassword())

    @on(Button.Pressed, "#view_accounts")
    def list_accounts(self) -> None:
        self.app.push_screen(ViewAccounts())

    @on(Button.Pressed, "#exit")
    def exit_app(self):
        print("Exiting...")
        self.app.exit()
    
    @on(Button.Pressed, "#test1")
    def display_text(self):
        input = self.query_one("#test", Input)
        text = input.value
        self.mount(Static(text))
        input.clear()


if __name__ == "__main__":
    passwords = load_passwords()
    app = PasswordPrompt()

    if 'login_pw' in passwords.keys():        
        app.run()
    else:
        print("Please set a password. This will be needed to access the app")
        pw1 = input("Enter a password: \n")
        pw2 = input("Enter password again: \n")
        if pw1 == pw2:
            key = load_key()
            add_password(key, 'login_pw', 'default_user', pw1)

            app.run()
        else:
            print("Passwords do not match. Please try again.")
