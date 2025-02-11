import flet as ft

class LanguageSwitcherApp:
    def __init__(self):  # Fixed: Changed _init_ to __init__
        self.translations = {
            "en": {
                "title": "Welcome to the App",
                "greeting": "Hello, how are you?",
                "button": "Switch to Portuguese",
                "info": "This is a simple bilingual app"
            },
            "ku": {  # Kurdish
                "title": "Bi xêr hatî ser Appê",
                "greeting": "Slav, tu çawa yî?",
                "button": "Bi inglîzî ve biguherîne",
                "info": "Ev app-a zimanê dîrokî ye"
            },
            "ar": {  # Arabic
                "title": "مرحبًا بك في التطبيق",
                "greeting": "مرحبًا، كيف حالك؟",
                "button": "التبديل إلى الإنجليزية",
                "info": "هذا تطبيق بسيط باللغات"
            }
        }
        self.current_language = "en"

    def main(self, page: ft.Page):
        page.title = "Language Switcher"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        def switch_language(e):
            if e.control.value:  # Check if value exists
                self.current_language = e.control.value  # Fixed: Use value directly
                
                # Update texts
                title.value = self.translations[self.current_language]["title"]
                greeting.value = self.translations[self.current_language]["greeting"]
                info.value = self.translations[self.current_language]["info"]
                page.update()

        # Create UI elements
        title = ft.Text(
            value=self.translations[self.current_language]["title"],
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER  # Added center alignment
        )
        
        greeting = ft.Text(
            value=self.translations[self.current_language]["greeting"],
            size=20,
            text_align=ft.TextAlign.CENTER
        )
        
        info = ft.Text(
            value=self.translations[self.current_language]["info"],
            size=16,
            text_align=ft.TextAlign.CENTER
        )
        
        # Language dropdown
        language_dropdown = ft.Dropdown(
            width=200,  # Added width for better appearance
            value=self.current_language,
            options=[
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ku", "Kurdish"),
                ft.dropdown.Option("ar", "Arabic")
            ],
            on_change=switch_language
        )

        # Add elements to page
        page.add(
            ft.Column(
                [
                    title,
                    ft.Container(height=20),
                    greeting,
                    ft.Container(height=10),
                    info,
                    ft.Container(height=20),
                    language_dropdown
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER  # Added vertical centering
            )
        )

if __name__ == "__main__":  # Fixed: Changed _name_ to __name__
    app = LanguageSwitcherApp()
    ft.app(target=app.main)