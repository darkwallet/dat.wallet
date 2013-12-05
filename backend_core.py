import obelisk
import sys
import threading

class Backend:

    def __init__(self, seed):
        self.wallet = obelisk.HighDefWallet.root(seed)
        self.key_index = 0
        self.client = obelisk.ObeliskOfLightClient('tcp://37.139.11.99:9091')
        self.addrs = {self.current_address: None}
        self.last_height = None

    def generate_key(self, n):
        key = obelisk.EllipticCurveKey()
        secret = self.wallet.branch(n).secret
        assert len(secret) == 32
        key.set_secret(secret)
        return key

    def generate_address(self, n):
        return self.wallet.branch(n).address

    def next_key(self):
        self.key_index += 1
        self.addrs[self.current_address] = None
        self.update()

    @property
    def current_address(self):
        return self.generate_address(self.key_index)

    def update(self, history_callback):
        self.poll_histories(history_callback)
        self.poll_height()

    def poll_histories(self, history_callback):
        for address in self.addrs.keys():
            def history_fetched(ec, history):
                self.history_fetched(ec, history, address, history_callback)
            self.client.fetch_history(address, history_fetched)

    def history_fetched(self, ec, history, address, history_callback):
        if ec != None:
            print >> sys.stderr, "Error fetching history:", ec
            return
        self.addrs[address] = history
        history_callback(address, history)

    def poll_height(self):
        def last_height_fetched(ec, last_height):
            if ec != None:
                print >> sys.stderr, "Error fetching last height:", ec
                return
            self.last_height = last_height
        self.client.fetch_last_height(last_height_fetched)

