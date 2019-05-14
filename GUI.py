import wx
import os
from Client import *

CLIENT = Client()


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.client = CLIENT

    def OnDropFiles(self, x, y, file_names):
        """
        When files are dropped, write where they were dropped and then the file paths themselves
        """
        self.window.SetInsertionPointEnd()
        self.window.updateText("\n{} file(s) dropped at ({},{})\n".format(len(file_names), x, y))
        for file_path in file_names:
            try:
                self.window.updateText(file_path + '\n')
                with open(file_path) as file:
                    # main loop do files here
                    print(file)
            except Exception as err:
                print(str(err))
        return True


class DnDPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        file_drop_target = MyFileDropTarget(self)
        lbl = wx.StaticText(self, label="Drag some files here:")
        self.fileTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
        self.fileTextCtrl.SetDropTarget(file_drop_target)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.fileTextCtrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def SetInsertionPointEnd(self):
        """
        Put insertion point at end of text control to prevent overwriting
        """
        self.fileTextCtrl.SetInsertionPointEnd()

    def updateText(self, text):
        """
        Write text to the text control
        """
        self.fileTextCtrl.WriteText(text)


class DnDFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="DropDrive")
        panel = DnDPanel(self)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = DnDFrame()
    app.MainLoop()
