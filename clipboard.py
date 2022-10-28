from threading import Thread
from time import sleep

import wx
import pyperclip


class UnsupportedOperation(Exception):
    """This exception is thrown in case an operation cannot be performed on the system"""

    def __init__(self, msg):
        super(UnsupportedOperation, self).__init__(msg)


def copy(content: str):
    """Write some text to the clipboard"""
    # try:
    #    if not wx.TheClipboard.IsOpened():
    #        wx.TheClipboard.Open()
    #        wx.TheClipboard.SetData(wx.TextDataObject(content))
    #        wx.TheClipboard.Close()
    # except:
    #    raise UnsupportedOperation("Your system does not have clipboard support")
    pyperclip.copy(content)


def paste() -> str:
    """Read some text"""
    # try:
    #    text_data = wx.TextDataObject()
    #    if not wx.TheClipboard.IsOpened():
    #        wx.TheClipboard.Open()
    #        success = wx.TheClipboard.GetData(text_data)
    #        wx.TheClipboard.Close()
    #    if success:
    #         return text_data.GetText()
    #    else:
    #        return None
    # except:
    #    raise UnsupportedOperation("Your system does not have clipboard support")
    return str(pyperclip.paste())


def clear():
    # if not wx.TheClipboard.IsOpened():
    #    wx.TheClipboard.Open()
    #    wx.TheClipboard.SetData(wx.TextDataObject(""))
    #    wx.TheClipboard.Flush()
    #    wx.TheClipboard.Close()
    copy("")


class ClipboardMonitor(Thread):
    """This class is in charge of processing the clipboard content to later be translated into another language."""

    def __init__(self):
        """This builder starts by requesting a content requester to submit the original and translated content"""
        super(ClipboardMonitor, self).__init__()
        self.__delay_time = 2
        self.__monitoring: bool = False

    def is_running(self) -> bool:
        """Returns the status of the monitor"""
        return self.__monitoring

    def start_monitoring(self) -> None:
        """Starts the thread to monitor the clipboard."""
        self.start()

    def stop_monitoring(self) -> None:
        """Stops the thread used to monitor the clipboard"""
        if self.is_running():
            self.__monitoring = False
        if self.is_alive():
            self.join()

    def invoke_translate(self, content: str, old: str):
        wx.CallAfter(self.__requester.set_content, "source", content)
        wx.CallAfter(self.__requester.set_content, "target", "Translating...")
        try:
            translated = self.__translator.translate(content)
            wx.CallAfter(self.__requester.set_content, "target", translated)
            copy(content)
            return content
        except Exception:
            return old

    def run(self):
        """This method implements the code necessary to keep the clipboard monitoring"""
        old_content = ""
        while self.is_running():
            clipboard_content: str = paste()
            if (clipboard_content is not None) and (clipboard_content.__len__() > 0):
                #clipboard_content = self.__formatter.format(clipboard_content)
                wx.CallAfter(self.__requester.set_number_characters, len(clipboard_content))
                if clipboard_content != old_content:
                    old_content = self.invoke_translate(clipboard_content, old_content)
                else:
                    if old_content == "":
                        old_content = self.invoke_translate(
                            clipboard_content, old_content
                        )
            sleep(self.__delay_time)
