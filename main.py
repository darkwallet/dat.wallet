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
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemLabel, ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.core.clipboard import Clipboard

from kivy.config import Config
# golden ratio
Config.set('graphics', 'width', 309)
Config.set('graphics', 'height', 500)
#Config.set('graphics', 'resizable', 0)

from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import task, reactor

from decimal import Decimal as D

import backend_core
import clipboard
import obelisk

class RootWidget(BoxLayout):
    pass


class BalanceSection(BoxLayout):

    def __init__(self, backend, **kwargs):
        super(BalanceSection, self).__init__(**kwargs)
        self.backend = backend

        main_layout = BoxLayout(orientation='horizontal')

        # TODO wire up the real amount to a formatter which gets fed here
        self.balance_label = Label(text='00.00 mBTC', font_size=28, bold=True)
        main_layout.add_widget(self.balance_label)

        self.add_widget(main_layout)

        # This is the shittiest method I can imagine to update balance.
        # don't do this ever.
        later = task.LoopingCall(self.recalc_balance)
        later.start(5)

    def recalc_balance(self):
        total_balance = 0
        for addr, history in self.backend.addrs.iteritems():
            total_balance += sum(row[3] for row in history
                                 if row[-1] == obelisk.MAX_UINT32)
        millis = D(total_balance) / 100000
        self.balance_label.text = "%.2f mBTC" % millis

class ReceiveSection(BoxLayout):

    def __init__(self, backend, **kwargs):
        super(ReceiveSection, self).__init__(**kwargs)
        self.backend = backend

        main_layout = BoxLayout(orientation='vertical')

        nextaddress_label = Label(text='click below to copy\nnext receive address',
            size_hint_y=0.5, font_size=20, halign='center')
        main_layout.add_widget(nextaddress_label)

        # TODO wire this text input up to a real address which may change when a transaction to this address occurs
        self.current_address = self.backend.current_address
        shortened_address = self.current_address[:6] + "..."
        nextaddress_input = Button(
            text=shortened_address,
            size_hint_y=0.3,
            font_size=20,
            foreground_color=(1,1,1,1))
        nextaddress_input.bind(on_press=self.copy_address_to_clipboard)
        nextaddress_input.next_address = self.current_address
        main_layout.add_widget(nextaddress_input)

        self.add_widget(main_layout)

    def copy_address_to_clipboard(self, instance):
        address = instance.next_address
        clipboard.copy(address)
        self.show_copied_popup(address)
        print Clipboard.get('UTF8_STRING')

    def show_copied_popup(self, address):
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

    def __init__(self, backend, **kwargs):
        super(SendSection, self).__init__(**kwargs)
        self.backend = backend

        self.main_layout = BoxLayout(orientation='vertical')

        self.sendaddress = TextInput(hint_text="Enter a payment address", size_hint_y=0.2, font_size=20)
        self.main_layout.add_widget(self.sendaddress)

        self.sendsection = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        self.amount_mbtc = TextInput(text='0', halign='right', font_size=20, padding=(20, 20))
        self.sendsection.add_widget(self.amount_mbtc)
        self.sendsection.add_widget(Label(text='mBTC', halign='left'))
        self.sendbutton = Button(text='Send')
        self.sendbutton.bind(on_press=self.call_send)
        self.sendsection.add_widget(self.sendbutton)

        self.main_layout.add_widget(self.sendsection)

        self.add_widget(self.main_layout)

    def call_send(self, instance):
        address = self.sendaddress.text
        amount_satoshis = D(self.amount_mbtc.text) * 10**5
        # debug
        address = "1Fufjpf9RM2aQsGedhSpbSCGRHrmLMJ7yY"
        amount_satoshis = 100000
        print 'should send', str(amount_satoshis) ,'to address', address
        # TODO validate address
        # TODO call backend send function
        optimal_outputs = self.backend.select_outputs(amount_satoshis)
        print optimal_outputs
        if optimal_outputs is None:
            self.show_invalid_balance_popup()
            return
        # Add inputs
        tx = obelisk.Transaction()
        for output in optimal_outputs.points:
            add_input(tx, output.point)
        add_output(tx, address, amount_satoshis)
        fee = 10000
        if optimal_outputs.change > fee:
            change = optimal_outputs.change - fee
            add_output(tx, self.backend.change_address, change)
        for i, output in enumerate(optimal_outputs.points):
            obelisk.sign_transaction_input(tx, i, output.key)
        print tx
        print tx.serialize().encode("hex")

    def show_invalid_balance_popup(self):
        btnclose = Button(text='Close this popup', size_hint_y=None, height='50sp')
        content = BoxLayout(orientation='vertical')
        row_length = 15
        content.add_widget(Label(text='Not enough money for send.'))
        content.add_widget(btnclose)
        popup = Popup(content=content, title='Not enough...',
                      size_hint=(None, None), size=('300dp', '300dp'))
        btnclose.bind(on_release=popup.dismiss)
        button = Button(text='Open popup', size_hint=(None, None),
                        size=('150sp', '70dp'),
                        on_release=popup.open)
        popup.open()
        col = AnchorLayout()
        col.add_widget(button)
        return col

def add_input(tx, prevout):
    input = obelisk.TxIn()
    input.previous_output.hash = prevout.hash
    input.previous_output.index = prevout.index
    tx.inputs.append(input)

def add_output(tx, address, value):
    output = obelisk.TxOut()
    output.value = int(value * 10**8)
    output.script = obelisk.output_script(address)
    tx.outputs.append(output)

class TransactionSection(BoxLayout):

    def __init__(self, backend, **kwargs):
        super(TranscationSection, self).__init__(**kwargs)       
        self.backend = backend
        self.transactions = [{'value': 'No transactions'}]

        main_layout = BoxLayout(orientation='vertical')

        self.transaction_history = self.make_transaction_widget()
        main_layout.add_widget(self.transaction_history)

        self.add_widget(main_layout)




    def make_transaction_widget(self):
        print 'make_transaction_widget called'
        args_converter = lambda row_index, rec: {'text': str(rec['value']),
                                         'size_hint_y': None,
                                         'height': 25}

        #self.transaction_history = ListView(item_strings=self.get_transactions(0,50))
        print self.transactions
        transaction_history = ListAdapter(data=self.transactions,
            args_converter=args_converter,
            cls=ListItemLabel,
            selection_mode='single',
            allow_empty_selection=False)

        #self.list_view.adapter = transaction_history
        list_view = ListView(adapter=transaction_history)
        return list_view


    def get_transactions(self, start=0, amount=100):
        print self.transactions
        #item_strings=[('row ' + str(index) + ': +500 mBTC sent to 1MNmTP...') for index in range(amount)]
        transaction_strings=[]
        for txhash, tx in self.transactions:
            if s_index != obelisk.MAX_UINT32:
                transaction_strings.append('+' + tx['value'] + ' satoshis received on ' + tx['address'])
            else:
                transaction_strings.append(tx['value'] + ' satoshis sent from ' + tx['addrdress'])

        print transaction_strings
        return transaction_strings

class MainApp(App):

    def __init__(self, backend):
        super(MainApp, self).   __init__()
        self.backend = backend
        self.transactions = []

    def cb(self, addr, history):
        # print addr, history
        for row in history:
            o_hash, o_index, o_height, value, s_hash, s_index, s_height = row
            if s_index != obelisk.MAX_UINT32:
                value = -value
            self.transactions.append({'address': addr, 'o_hash': o_hash.encode('hex'), 'o_index': o_index, 'o_height': o_height, 'value': value,
            's_hash': s_hash.encode("hex"), 's_index': s_index, 's_height': s_height})

        #self.trans.transaction_history.add_node(TreeViewLabel(text=str(value) + ' satoshis sent to/from ' + addr))
        self.trans.transactions = self.transactions
        #self.trans.remove_widget(self.trans.transaction_history)
        self.trans.transaction_history = self.trans.make_transaction_widget()
        #self.trans.add_widget(self.trans.transaction_history)

        #print self.transactions

    def build(self):
        root = RootWidget()

        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(BalanceSection(backend=self.backend, size_hint_y=0.4))
        main_layout.add_widget(ReceiveSection(backend=self.backend, size_hint_y=1))
        main_layout.add_widget(SendSection(backend=self.backend, size_hint_y=0.7))
        self.trans = TransactionSection(backend=self.backend, size_hint_y=1)
        main_layout.add_widget(self.trans)

        root.add_widget(main_layout)

        later = task.LoopingCall(self.backend.update, self.cb)
        later.start(5)

        return root

if __name__ == '__main__':
    if len(sys.argv) == 1: sys.argv[1:] = ["correct horse battery staple"]
    print "\n".join(sys.argv)

    #import mnemonic
    #seedphrase = mnemonic.mn_decode(sys.argv[1])
    seed = "945d3c0e7b2343f327f1c6ec900e5406"
    print seed.encode("hex")
    backend = backend_core.Backend(seed)
    MainApp(backend).run()

