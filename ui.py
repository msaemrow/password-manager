from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Input, Static
from textual.screen import Screen

from storage import add_password, get_password
from encryption import load_key

class PasswordManagerApp(App):
    """Textual UI for Password Manager main page"""
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
            if event.button.id == "add_password":
                await self.push_screen(AddPasswordScreen())
            elif event.button.id == "get_password":
                await self.push_screen(GetPasswordScreen())
            elif event.button.id == "exit":
                self.exit()

class AddPasswordScreen(Screen):
    def compose(self):
        yield Horizontal(
            VerticalScroll(
                Header("Add new password", classes="header"),
                Input(placeholder="Service", id="add_account", classes="pw_input"),
                Input(placeholder="Username", id="add_username",classes="pw_input"),
                Input(placeholder="Password", id="add_password", classes="pw_input", password=True),
                Input(placeholder="Confirm Password", id="confirm_password", classes="pw_input", password=True)
            ),
            Horizontal(
                Button("Add Combination", id="submit", variant="success", classes="button" ),
                Button("Main Menu", id="exit", variant="success", classes="button" ),
                Button("Test Button", id="test", variant="success", classes="button")
            ),
        )
        yield Footer()

    
    async def on_button_click(self, event: Button.Pressed) -> None:
        """Handles button clicks on AddPasswordScreen"""
        self.notify(f"Button Pressed: {event.button.id}", severity="warning")

        account = self.query_one("#add_account", Input).value.strip()
        username = self.query_one("#add_username", Input).value.strip()
        password = self.query_one("#add_password", Input).value.strip()
        confirm_password = self.query_one("#confirm_password", Input).value.strip()
        if event.button.id == "submit":


            if not(account and username and password and confirm_password):
                self.notify("All fields are required", severity="error")
                return
           
            if password != confirm_password:
                self.notify("Passwords must match", severity="eror")

            key=load_key()
            await add_password(key, account, username, password)
            self.notify("Password added successfully", severity="success")
            await self.app.pop_screen()

        elif event.button.id == "exit":
                self.notify("Returning to main menu...", severity="information")
                await self.app.pop_screen()

class GetPasswordScreen(Screen):
    def compose(self):
        yield Vertical(
            Header("Look Up Password", classes="header"),
            Input(placeholder="Enter Account Name", id="account_name", classes="pw_input"),
            Horizontal(
                Button("Submit", id="submit", variant="success", classes="button"),
                Button("Main Menu", id="exit", variant="secondary", classes="button")
            ),
        )
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles password retrieval"""
        if event.button.id == "submit":
            account = self.query_one("#account_name", Input).value.strip()

            if not account:
                self.notify("Must enter account name", severity="error")
                return
            
            key=load_key()

            result = get_password(account, key)
            if result:
                    username, password = result
                    self.notify(f"Service: {account}\nUsername: {username}\nPassword: {password}")
            else:
                self.notify(f"No password found for {account}")
        elif event.button.id == "exit":
             await self.app.pop_screen()
        

    if __name__ == "__main__":
        PasswordManagerApp().run()