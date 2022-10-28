import copy
import sqlite3
import sys
from io import StringIO
import wx
import wx.html2
from ansi2html import Ansi2HTMLConverter
from cambridge import cache
from cambridge.args import parse_args
import pyperclip
import threading


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

        sizer = wx.BoxSizer(wx.VERTICAL)
        # btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.browser = wx.html2.WebView.New(self)

        # btn_translate = wx.Button(self, -1, "Translate")
        # btn_translate.Bind(wx.EVT_BUTTON, self.btn_translate_on_clicked)
        # btn_sizer.Add(btn_translate, 0, wx.ALIGN_CENTER)

        # sizer.Add(btn_sizer, 0, wx.EXPAND)
        sizer.Add(self.browser, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.conv = Ansi2HTMLConverter()

        self.word = ''
        self.old_word = ''
        self.default_argv = copy.deepcopy(sys.argv)
        self.btn_translate_on_clicked()

    @set_interval(3)
    def btn_translate_on_clicked(self):
        self.word = pyperclip.paste()
        if not self.word or self.old_word == self.word:
            return
        self.old_word = self.word
        sys.argv = copy.deepcopy(self.default_argv)
        stream = StringIO()
        sys.stdout = stream

        self.translate('cambridge')
        self.translate('webster')
        html = self.conv.convert(stream.getvalue())
        self.browser.SetPage(html, "")
        sys.stdout = sys.__stdout__

    def translate(self, dictionary):
        cache_db = "cambridge.db"
        if dictionary == 'webster':
            sys.argv.append('-w')
            cache_db = "webster.db"
        else:
            sys.argv += [self.word]
        con = sqlite3.connect(
            str(cache.dir / cache_db), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        args = parse_args()
        args.func(args, con, cur)
        cur.close()
        con.close()


if __name__ == '__main__':
    app = wx.App()
    window = wx.Frame(None, -1, "Translators", wx.DefaultPosition, size=(800, 800))
    panel = AppPanel(window)
    window.Show()
    app.MainLoop()
