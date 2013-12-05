module = None
try:
    import clipboard_macosx
    module = "mac"
except ImportError:
    from kivy.core.clipboard import Clipboard
    module = "kivy"

def copy(data):
    if module == "mac":
        clipboard_macosx.copy(data)
    else:
        assert module == "kivy"
        Clipboard.put(data, 'UTF8_STRING')

