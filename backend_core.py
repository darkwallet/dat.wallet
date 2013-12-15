import obelisk
import sys
import threading
import urllib2, re, random

# Makes a request to a given URL (first argument) and optional params (second argument)
def make_request(*args):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0'+str(random.randrange(1000000)))]
    try:
        return opener.open(*args).read().strip()
    except Exception,e:
        try: p = e.read().strip()
        except: p = e
        raise Exception(p)

def bci_pushtx(tx):
    return make_request('http://blockchain.info/pushtx','tx='+tx)

def eligius_pushtx(tx):
    s = make_request('http://eligius.st/~wizkid057/newstats/pushtxn.php','transaction='+tx+'&send=Push')
    strings = re.findall('string[^"]*"[^"]*"',s)
    for string in strings:
        quote = re.findall('"[^"]*"',string)[0]
        if len(quote) >= 5: return quote[1:-1]

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
        self.keys = {
            self.current_address: self.current_key,
            self.current_change_address: self.current_change_key}
        self.last_height = None

    def generate_key(self, n):
        key = obelisk.EllipticCurveKey()
        secret = self.wallet.branch(n).secret
        assert len(secret) == 32
        key.set_secret(secret)
        return key

    def generate_change_key(self, n):
        key = obelisk.EllipticCurveKey()
        secret = self.wallet.branch_prime(n).secret
        assert len(secret) == 32
        key.set_secret(secret)
        return key

    def generate_address(self, n):
        return self.wallet.branch(n).address

    def next_key(self):
        self.key_index += 1
        self.addrs[self.current_address] = []
        self.addrs[self.current_change_address] = []
        self.keys[self.current_address] = self.current_key
        self.keys[self.current_change_address] = self.current_change_key

    @property
    def current_key(self):
        return self.generate_key(self.key_index)

    @property
    def current_change_key(self):
        return self.generate_change_key(self.key_index)

    @property
    def current_address(self):
        return self.generate_address(self.key_index)

    @property
    def current_change_address(self):
        key = obelisk.EllipticCurveKey()
        return self.wallet.branch_prime(self.key_index).address

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

    def broadcast(self, tx):
        raw_tx = tx.serialize().encode("hex")
        print "Tx data:", raw_tx
        eligius_pushtx(raw_tx)
        bci_pushtx(raw_tx)

