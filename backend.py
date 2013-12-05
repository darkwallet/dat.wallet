import obelisk

class Backend:

    def __init__(self, seed):
        self.wallet = obelisk.HighDefWallet.root(seed)
        self.key_index = 0

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

    @property
    def current_address(self):
        return self.generate_address(self.key_index)

