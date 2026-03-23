from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.chip import MDChip, MDChipLeadingIcon, MDChipText
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.list import MDList, MDListItem, MDListItemLeadingIcon, MDListItemSupportingText

from kivymd.app import MDApp
from kivymd.uix.card import MDCard


class GameCard(MDCard):
    '''Implements a material card.'''
    title = StringProperty('')
    genres = ListProperty([])
    date = StringProperty('')
    rating = StringProperty('')
    platforms = ListProperty([])

    source = StringProperty('')
    platforms_display_text = StringProperty('')
    platform_icon = StringProperty('')

    icon_map = {
        'PC': 'microsoft-windows',
        'PS4': 'sony-playstation',
        'Xbox One': 'microsoft-xbox',
        'Switch': 'nintendo-switch',
        'Mobile': 'android',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(platforms=self._update_platforms_display)
        self._dialog = None

    def _update_platforms_display(self, *args):
        """Update chip text based on platforms list."""

        if not self.platforms:
            self.platforms_display_text = ''
        elif len(self.platforms) == 1:
            self.platforms_display_text = self.platforms[0]
        else:
            self.platforms_display_text = f"+{len(self.platforms)-1}"
        self.platform_icon = self.icon_map.get(self.platforms[0], 'gamepad-variant')

    def show_platforms_dialog(self):
        """Open a dialog with the full list of platforms."""
        if not self.platforms or self._dialog:
            return

        # Icon mapping (same as before)

        # Create list items
        list_items = []
        for platform in self.platforms:
            icon = self.icon_map.get(platform, 'gamepad-variant')
            item = MDListItem(
                MDListItemLeadingIcon(icon=icon),
                MDListItemSupportingText(text=platform.capitalize()),
                theme_bg_color="Custom",
                md_bg_color=self.theme_cls.transparentColor,  # Use theme transparent color
                size_hint_y=None,
                height=dp(48),
            )
            list_items.append(item)

        # Build dialog
        self._dialog = MDDialog(
            # --- Headline ---
            MDDialogHeadlineText(
                text="Платформы",
                halign="left",
            ),
            # --- Content Container (the list) ---
            MDDialogContentContainer(
                *list_items,  # Unpack the list items
                orientation="vertical",
                spacing="4dp",
            ),
            # --- Button Container (optional close button) ---
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Закрыть"),
                    style="text",
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                spacing="8dp",
            ),
            # --- Dialog properties ---
            auto_dismiss=True,  # Allow closing by clicking outside
            size_hint=(0.8, None),
            height=dp(400),  # Fixed height, but will adapt to content
        )
        self._dialog.open()
        # Clean up reference when closed
        self._dialog.bind(on_dismiss=lambda *x: setattr(self, '_dialog', None))

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self._update_platforms_display()

class Example(MDApp):
    def build(self):
        return Builder.load_file('.\kv\game.kv')

    def on_start(self):
        self.root.ids.box.add_widget(GameCard(
            title='Readsdnk dsadasdasd 2',
            genres=['RPG'],
            date='23.01.2001',
            rating=str(9.0),
            platforms=['PC'],
            source=f"{2}.jpg"
        ))


if __name__ == '__main__':
    Example().run()
