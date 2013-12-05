from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView
#from kivy.uix.dropdown import DropDown

from kivy.config import Config
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '600')

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

# def on_enter(instance, value):
#     print('User pressed enter in', instance)

class MainApp(App):

    def build(self):
        root = RootWidget()

        main_layout = BoxLayout(orientation='vertical')

        # balance section
        balance = BoxLayout(orientation='horizontal')
        balance.add_widget(Label(text='Balance', halign='right'))
        balance.add_widget(Label(text='1,276.00 mBTC'))
        main_layout.add_widget(balance)
        #end balance section

        # next address section
        nextaddress_label = Label(text='next receive address')
        main_layout.add_widget(nextaddress_label)

        nextaddress_input = TextInput(
            text='1MNmTPTRp9g4ruE5Hw7kb2AZuaRpVLwGta',
            multiline=False,
            readonly=True,
            #halign='center',
            size_hint=(1, 0.5),
            font_size=20,
            background_color=(0, 0, 0, 1),
            foreground_color=(1, 1, 1, 1))
        # could implement clipboard copy here or convert to Button
        # nextaddress_input.bind(on_text_validate=on_enter)
        main_layout.add_widget(nextaddress_input)
        # end next address section

        # send section
        sendaddress = TextInput(text="1abcdef...")
        main_layout.add_widget(sendaddress)

        sendsection = BoxLayout(orientation='horizontal')
        sendsection.add_widget(TextInput(text='125', halign='right'))
        #dropdown = DropDown()
        #sendsection.add_widget()
        sendsection.add_widget(Button(text='Send'))
        main_layout.add_widget(sendsection)
        # end send section

        # transaction section
        # TODO populate this list with real transaction data
        transaction_history = ListView(
            item_strings=[str(index) for index in range(100)])
        main_layout.add_widget(transaction_history)
        # end transaction section

        root.add_widget(main_layout)

        return root

if __name__ == '__main__':
    MainApp().run()
