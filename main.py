from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView
from kivy.core.clipboard import Clipboard

from kivy.config import Config
# golden ratio
Config.set('graphics', 'width', '309')
Config.set('graphics', 'height', '500')

import clipboard

class RootWidget(BoxLayout):
    pass

class CustomLayout(FloatLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0, 1, 0, 1) # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(
                            size=self.size,
                            pos=self.pos)

        self.bind(
                    size=self._update_rect,
                    pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

def get_transactions(start=0, amount=100):
    item_strings=[('+500 mBTC sent to ' + str(index)) for index in range(amount)]

    return item_strings

def copy_address_to_clipboard(instance):
    clipboard.copy(instance.next_address)
    print Clipboard.get('UTF8_STRING')



class SendSection(BoxLayout):
    def __init__(self, **kwargs):
        super(SendSection, self).__init__(**kwargs)

        self.main_layout = BoxLayout(orientation='vertical')

        self.sendaddress = TextInput(hint_text="Enter a payment address", size_hint_y=0.2, font_size=20)
        #self.main_layout(self.sendaddress)
        self.add_widget(self.sendaddress)

        self.sendsection = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        self.amount_mbtc = TextInput(text='125', halign='right', font_size=20, padding=(20, 20))
        self.sendsection.add_widget(self.amount_mbtc)
        self.sendsection.add_widget(Label(text='mBTC', halign='left'))
        self.sendbutton = Button(text='Send')
        self.sendbutton.bind(on_press=self.call_send)
        self.sendsection.add_widget(self.sendbutton)

        #self.main_layout(self.sendsection)
        #self.add_widget(main_layout)
        self.add_widget(self.sendsection)

    def call_send(self, instance):
        print 'got address ', self.sendaddress.text, 'with amount ', str(self.amount_mbtc.text)
        # TODO validate address
        # TODO call backend send function


        self.bind(
                    size=self._update_rect,
                    pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class MainApp(App):

    def build(self):
        root = RootWidget()

        main_layout = BoxLayout(orientation='vertical')

        ### balance section
        balance = BoxLayout(orientation='horizontal', size_hint_y=0.6)
        # TODO wire up the real amount to a formatter which gets fed here
        balance.add_widget(Label(text='1,276.00 mBTC', font_size=28, bold=True))
        main_layout.add_widget(balance)
        ### end balance section

        ### next address section
        nextaddress_label = Label(text='click below to copy\nnext receive address',
            size_hint_y=0.5, font_size=20, halign='center')
        main_layout.add_widget(nextaddress_label)

        # TODO wire this text input up to a real address which may change when a transaction to this address occurs
        next_address = '1MNmTPTRp9g4ruE5Hw7kb2AZuaRpVLwGta'
        nextaddress_input = Button(
            text='1MNmTP...VLwGta',
            size_hint_y=0.3,
            font_size=20,
            foreground_color=(1,1,1,1))
        nextaddress_input.bind(on_press=copy_address_to_clipboard)
        nextaddress_input.next_address = next_address
        main_layout.add_widget(nextaddress_input)
        ### end next address section

        main_layout.add_widget(SendSection())

        # ##transaction section
        # TODO populate this list with real transaction data
        transaction_history = ListView(item_strings=get_transactions(0,100))
        main_layout.add_widget(transaction_history)
        ### end transaction section

        root.add_widget(main_layout)

        return root

if __name__ == '__main__':
    MainApp().run()
