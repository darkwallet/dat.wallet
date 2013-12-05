import sys
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard

from kivy.config import Config
# golden ratio
Config.set('graphics', 'width', '309')
Config.set('graphics', 'height', '500')

import backend
import clipboard

class RootWidget(BoxLayout):
    pass


def get_transactions(start=0, amount=100):
    item_strings=[('+500 mBTC sent to 1MNmTP...') for index in range(amount)]

    return item_strings

def copy_address_to_clipboard(instance):
    address = instance.next_address
    clipboard.copy(address)
    show_copied_popup(address)
    print Clipboard.get('UTF8_STRING')

def show_copied_popup(address):
    btnclose = Button(text='Close this popup', size_hint_y=None, height='50sp')
    content = BoxLayout(orientation='vertical')
    row_length = 15
    for i in range(0, len(address), row_length):
        content.add_widget(Label(text=address[i:i + row_length]))
    content.add_widget(btnclose)
    popup = Popup(content=content, title='Copied Address',
                  size_hint=(None, None), size=('300dp', '300dp'))
    btnclose.bind(on_release=popup.dismiss)
    button = Button(text='Open popup', size_hint=(None, None),
                    size=('150sp', '70dp'),
                    on_release=popup.open)
    popup.open()
    col = AnchorLayout()
    col.add_widget(button)
    return col

class SendSection(BoxLayout):
    def __init__(self, **kwargs):
        super(SendSection, self).__init__(**kwargs)

        self.main_layout = BoxLayout(orientation='vertical')

        self.sendaddress = TextInput(hint_text="Enter a payment address", size_hint_y=0.2, font_size=20)
        self.main_layout.add_widget(self.sendaddress)

        self.sendsection = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        self.amount_mbtc = TextInput(text='125', halign='right', font_size=20, padding=(20, 20))
        self.sendsection.add_widget(self.amount_mbtc)
        self.sendsection.add_widget(Label(text='mBTC', halign='left'))
        self.sendbutton = Button(text='Send')
        self.sendbutton.bind(on_press=self.call_send)
        self.sendsection.add_widget(self.sendbutton)

        self.main_layout.add_widget(self.sendsection)

        self.add_widget(self.main_layout)

    def call_send(self, instance):
        toaddress = self.sendaddress.text
        # precision of float() ?
        amount_satoshis = float(self.amount_mbtc.text) * 1e5
        print 'should send', str(amount_satoshis) ,'to address ', toaddress
        # TODO validate address
        # TODO call backend send function

class MainApp(App):

    def build(self):
        self.backend = backend.Backend(seedphrase)
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
        current_address = self.backend.current_address
        shortened_address = current_address[:6] + "..."
        nextaddress_input = Button(
            text=shortened_address,
            size_hint_y=0.3,
            font_size=20,
            foreground_color=(1,1,1,1))
        nextaddress_input.bind(on_press=copy_address_to_clipboard)
        nextaddress_input.next_address = current_address
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
    if len(sys.argv) == 1: sys.argv[1:] = ["correct horse battery staple"]
    print "\n".join(sys.argv)

    seedphrase = sys.argv[1].encode("hex")
    print seedphrase
    MainApp().run()
