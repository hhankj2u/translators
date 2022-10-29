import sqlite3
import threading
import pyperclip
import wx
import wx.html2
from core import cache
from core.dicts import cambridge, webster
from core.settings import DICTS, CAMBRIDGE, WEBSTER


# https://stackoverflow.com/a/16368571/6408343
def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):  # until stopped
                    try:
                        function(*args, **kwargs)
                    except Exception:
                        pass

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped

        return wrapper

    return decorator


class AppPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.browser_cambridge = wx.html2.WebView.New(self)
        self.browser_webster = wx.html2.WebView.New(self)

        sizer.Add(self.browser_cambridge, 1, wx.EXPAND)
        sizer.Add(self.browser_webster, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.word = 'banana'
        self.old_word = ''
        self.interval_translate_clipboard()

    @set_interval(2)
    def interval_translate_clipboard(self):
        self.word = pyperclip.paste()
        if not self.word or self.old_word == self.word:
            return
        self.old_word = self.word

        url, soup = self.translate(DICTS[CAMBRIDGE])
        self.browser_cambridge.SetPage(str(soup), url)
        url, soup = self.translate(DICTS[WEBSTER])
        self.browser_webster.SetPage(str(soup), url)

    def translate(self, dictionary):
        con = sqlite3.connect(
            str(cache.dir / dictionary), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        if dictionary == DICTS[CAMBRIDGE]:
            url, soup = cambridge.search_cambridge(con, cur, self.word)
        else:
            url, soup = webster.search_webster(con, cur, self.word)

        cur.close()
        con.close()

        return url, soup


if __name__ == '__main__':
    app = wx.App()
    window = wx.Frame(None, -1, "Translators", wx.DefaultPosition, size=(1000, 800))
    panel = AppPanel(window)
    window.Show()
    app.MainLoop()
