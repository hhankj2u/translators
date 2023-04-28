import sqlite3
import threading
import pyperclip
import wx
import wx.html2
from core import cache
from core.dicts import cambridge, webster, soha
from core.settings import DICTS, CAMBRIDGE, WEBSTER, SOHA


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

        sizer_container = wx.BoxSizer(wx.VERTICAL)
       
        sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_input = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER)
        self.txt_input.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPressed)        
        sizer_top.Add(self.txt_input, -1, wx.EXPAND)
        self.cb_disable = wx.CheckBox(self, label = 'Disable Ctrl+C')
        self.Bind(wx.EVT_CHECKBOX, self.onChecked) 
        sizer_top.Add(self.cb_disable, 0)
        sizer_container.Add(sizer_top, 0, wx.EXPAND)

        self.browser_cambridge = wx.html2.WebView.New(self)
        self.browser_webster = wx.html2.WebView.New(self)
        self.browser_soha = wx.html2.WebView.New(self)

        sizer_result = wx.BoxSizer(wx.HORIZONTAL)
        sizer_result.Add(self.browser_cambridge, 1, wx.EXPAND)
        sizer_result.Add(self.browser_webster, 1, wx.EXPAND)
        sizer_result.Add(self.browser_soha, 1, wx.EXPAND)
        sizer_container.Add(sizer_result, 1, wx.EXPAND)

        self.SetSizer(sizer_container)        

        self.word = 'banana'
        self.old_word = ''
        self.is_disable_auto = True # TODO:ddsfsdfsdf

        # init
        self.interval_translate_clipboard()

    @set_interval(2)
    def interval_translate_clipboard(self):
        if self.is_disable_auto == False:
            self.word = pyperclip.paste()

        if not self.word or self.old_word == self.word:
            return
        self.old_word = self.word

        url, soup = self.translate(DICTS[CAMBRIDGE])
        self.browser_cambridge.SetPage(str(soup), url)
        url, soup = self.translate(DICTS[WEBSTER])
        self.browser_webster.SetPage(str(soup), url)
        url, soup = self.translate(DICTS[SOHA])
        self.browser_soha.SetPage(str(soup), url)
    
    def translate(self, dictionary):
        con = sqlite3.connect(
            str(cache.dir / dictionary), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        if dictionary == DICTS[CAMBRIDGE]:
            url, soup = cambridge.search_cambridge(con, cur, self.word)
        elif dictionary == DICTS[WEBSTER]:
            url, soup = webster.search_webster(con, cur, self.word)
        elif dictionary == DICTS[SOHA]:
            url, soup = soha.search_soha(con, cur, self.word)

        cur.close()
        con.close()

        return url, soup

    def OnEnterPressed(self, event):
        self.word = event.GetString()
        self.interval_translate_clipboard()
        print(f"Enter pressed: {self.word}")

    def onChecked(self, e): 
      cb = e.GetEventObject() 
      print(cb.GetLabel(), ' is clicked', cb.GetValue())
      self.is_disable_auto = cb.GetValue()

if __name__ == '__main__':
    app = wx.App()
    window = wx.Frame(None, -1, "Translators", wx.DefaultPosition, size=(1000, 800))
    panel = AppPanel(window)
    window.Show()
    app.MainLoop()
