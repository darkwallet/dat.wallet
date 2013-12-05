# dat.wallet

## Installation
You will need:

    $ mkdir depends
    $ cd depends
    $ git clone https://github.com/caedesvvv/zmqproto.git
    $ git clone https://github.com/darkwallet/python-obelisk.git
    $ cd ..
    $ ln -s depends/zmqproto/zmqproto .
    $ ln -s depends/python-obelisk/obelisk .

These parent path where these repos are cloned will need to be added to
your PYTHONPATH environment variable.

    $ export PYTHONPATH=$PYTHONPATH:$(pwd)



# Usage
    kivy main.py -- "correct horse battery staple"

Where "correct horse battery staple" is your seed phrase. Note the space between the -- and the seed phrase
