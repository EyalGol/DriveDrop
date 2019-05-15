import wx
import os
from threading import Thread
from Client import *

CLIENT = None


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
                print(file_path)
                if file_path == file_names[-1]:
                    CLIENT.send_file(file_path, True)
                else:
                    CLIENT.send_file(file_path, False)

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


class LoginDialog(wx.Dialog):
    """
        Class to define login dialog
        """
    def __init__(self):
        wx.Dialog.__init__(self, None, title="Login")

        # user info
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        user_sizer.Add(self.user, 0, wx.ALL, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)

        p_lbl = wx.StaticText(self, label="Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        p_sizer.Add(self.password, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(user_sizer, 0, wx.ALL, 5)
        main_sizer.Add(p_sizer, 0, wx.ALL, 5)

        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.onLogin)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def onLogin(self, event):
        """
                   Check credentials and init client
                   """
        global CLIENT
        CLIENT = Client()
        stupid_password = "pas1234"
        user_name = self.user.GetValue()
        user_password = self.password.GetValue()
        if user_password == stupid_password:
            self.Destroy()


class Window(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "DropDrive")
        # def panels
        self.dnd_panel = DnDPanel(self)
        #self.login_panel = LoginPanel(self)
        #self.dnd_panel.Hide()

        # menu init
        self.menu_init()

        # sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.dnd_panel, 1, wx.EXPAND)
        #self.sizer.Add(self.login_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Show()
        login = LoginDialog()
        login.ShowModal()

    def menu_init(self):
        # Setting up the menu.
        file_menu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menu_about = file_menu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menu_exit = file_menu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
        #switch_panels_menu_item = file_menu.Append(wx.ID_ANY, "Switch Panels", "Login to FTP")

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")  # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.on_about, menu_about)
        self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
        #self.Bind(wx.EVT_MENU, self.on_switch_panels, switch_panels_menu_item)

    #def on_switch_panels(self, event):
    #    # switch panels (login/ftp)
    #    if self.dnd_panel.IsShown():
    #        self.SetTitle("Panel Two Showing")
    #        self.dnd_panel.Hide()
    #        self.login_panel.Show()
    #    else:
    #        self.SetTitle("Panel One Showing")
    #        self.dnd_panel.Show()
    #        self.login_panel.Hide()
    #    self.Layout()

    def on_about(self, e):
        # A message dialog box with an OK button.
        dlg = wx.MessageDialog(self, "This is DriveDrop its like google drive but worse", "About DriveDrop")
        dlg.ShowModal()
        dlg.Destroy()
#
    def on_exit(self, e):
        self.Close(True)


if __name__ == "__main__":
    app = wx.App(False)
    frame = Window()
    app.MainLoop()
    CLIENT.socket.close()
