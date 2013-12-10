import obelisk
import sys
import threading

class OutputInfoPlusKey(obelisk.OutputInfo):

    def __init__(self, point, value, key):
        super(OutputInfoPlusKey, self).__init__(point, value)
        self.key = key

def build_output_info_list(unspent_rows, key):
    unspent_infos = []
    for row in unspent_rows:
        assert len(row) == 4
        outpoint = obelisk.OutPoint()
        outpoint.hash = row[0]
        outpoint.index = row[1]
        value = row[3]
        unspent_infos.append(
            OutputInfoPlusKey(outpoint, value, key))
    return unspent_infos

class Backend:

    def __init__(self, seed):
        self.wallet = obelisk.HighDefWallet.root(seed)
        self.key_index = 0
        self.client = obelisk.ObeliskOfLightClient('tcp://37.139.11.99:9091')
        self.addrs = {self.current_address: []}
        self.keys = {self.current_address: self.current_key}
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
        self.addrs[self.current_address] = []
        self.keys[self.current_address] = self.current_key
        self.update()

    @property
    def current_key(self):
        return self.generate_key(self.key_index)

    @property
    def current_address(self):
        return self.generate_address(self.key_index)

    @property
    def change_address(self):
        key = obelisk.EllipticCurveKey()
        secret = self.wallet.branch_prime(self.key_index)
        assert len(secret) == 32
        key.set_secret(secret)
        return key

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

    def select_outputs(self, min_value):
        unspent = []
        for addr, history in self.addrs.iteritems():
            key = self.keys[addr]
            unspent_rows = [row[:4] for row in history
                            if row[5] == obelisk.MAX_UINT32]
            unspent.extend(build_output_info_list(unspent_rows, key))
        print unspent
        return obelisk.select_outputs(unspent, min_value)

