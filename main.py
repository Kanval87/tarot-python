import kivy
import json
kivy.require("2.0.0")

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
import random
import json
import os


class TarotCard(BoxLayout):
    def __init__(self, card_name, img_orientation, description, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=5, **kwargs)
        if img_orientation == "upright":
            image_path = f"tarot_cards/{card_name}.png"
        else:
            image_path = f"tarot_cards/{card_name} - Copy.png"

        self.card_name = card_name
        self.description = description

        self.image = Image(source=image_path, allow_stretch=True, keep_ratio=True)
        self.add_widget(self.image)

        self.detail_button = Button(text="Details", size_hint_y=None, height=30)
        self.detail_button.bind(on_release=self.show_details)
        self.add_widget(self.detail_button)

    def show_details(self, instance):
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup

        box = BoxLayout(orientation='vertical', padding=10)
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(
            text=f"{self.card_name} ({self.orientation.capitalize()}):\n\n{json.dumps(self.description, indent=2, ensure_ascii=False)}",
            size_hint_y=None, halign='left', valign='top'
        )
        label.bind(texture_size=lambda instance, value: setattr(label, 'height', value[1]))
        label.text_size = (600, None)
        scroll.add_widget(label)
        box.add_widget(scroll)
        popup = Popup(title="Card Details", content=box, size_hint=(0.9, 0.7))
        popup.open()

class TarotApp(App):
    def build(self):
        self.card_layout = GridLayout(cols=3, spacing=10, padding=10)
        self.selected_cards_label = TextInput(
            text="",
            size_hint_y=None,
            height=80,
            readonly=True,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            cursor_blink=False,
            font_size=16,
            multiline=True
        )
        self.selected_cards_label.text_size = (Window.width, None)
        main_layout = BoxLayout(orientation='vertical')
        # Add min/max range dropdowns
        with open("tarot_data.json", "r") as f:
            self.tarot_data = json.load(f)
        num_cards_total = len(self.tarot_data)
        card_range = [str(i) for i in range(1, num_cards_total + 1)]
        range_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10, padding=5)
        self.min_spinner = Spinner(
            text="1",
            values=card_range,
            size_hint_x=None,
            width=80
        )
        self.max_spinner = Spinner(
            text="6" if num_cards_total >= 6 else str(num_cards_total),
            values=card_range,
            size_hint_x=None,
            width=80
        )
        range_layout.add_widget(Label(text="Min:", size_hint_x=None, width=40))
        range_layout.add_widget(self.min_spinner)
        range_layout.add_widget(Label(text="Max:", size_hint_x=None, width=40))
        range_layout.add_widget(self.max_spinner)
        main_layout.add_widget(range_layout)
        # Create a horizontal box for label and button
        label_button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
        label_button_layout.add_widget(self.selected_cards_label)
        copy_button = Button(text='Copy', size_hint_x=None, width=80)
        copy_button.bind(on_release=self.copy_selected_cards)
        label_button_layout.add_widget(copy_button)
        main_layout.add_widget(label_button_layout)
        main_layout.add_widget(self.card_layout)
        Window.bind(on_key_down=self.on_key_down)

        return main_layout

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:  # Enter key
            self.select_cards()

    def select_cards(self):
        self.card_layout.clear_widgets()
        # Get min/max from dropdowns, with validation
        try:
            min_cards = int(self.min_spinner.text)
        except ValueError:
            min_cards = 1
        try:
            max_cards = int(self.max_spinner.text)
        except ValueError:
            max_cards = len(self.tarot_data)
        min_cards = max(1, min_cards)
        max_cards = min(len(self.tarot_data), max_cards)
        if min_cards > max_cards:
            min_cards, max_cards = max_cards, min_cards
        num_cards = random.randint(min_cards, max_cards)
        selected = random.sample(list(self.tarot_data.keys()), num_cards)
        # Update the label to show selected cards
        display_names = []
        for card in selected:
            orientation = random.choice(["upright", "reversed"])
            description = self.tarot_data[card][orientation]
            card_widget = TarotCard(card, orientation, description)
            self.card_layout.add_widget(card_widget)
            name = card
            if orientation == "reversed":
                name += " (Reversed)"
            display_names.append(name)
        self.selected_cards_label.text = "Pulled : " + ", ".join(display_names)

    def copy_selected_cards(self, instance):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.selected_cards_label.text)

if __name__ == "__main__":
    TarotApp().run()