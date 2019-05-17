import wx
import wx.xrc

from Client import *

CLIENT = None


class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(820, 500), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))

        frame_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.send_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        send_sizer = wx.BoxSizer(wx.VERTICAL)

        self.send_title = wx.StaticText(self.send_panel, wx.ID_ANY, u"Drag And Drop To Send File(s)",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.send_title.Wrap(-1)
        send_sizer.Add(self.send_title, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.send_file_text = wx.TextCtrl(self.send_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                          wx.DefaultSize, wx.TE_MULTILINE | wx.TE_READONLY)
        self.send_file_text.SetDropTarget(MyFileDropTarget(self.send_file_text))
        send_sizer.Add(self.send_file_text, 1, wx.ALL | wx.EXPAND, 5)

        self.send_panel.SetSizer(send_sizer)
        self.send_panel.Layout()
        send_sizer.Fit(self.send_panel)
        main_sizer.Add(self.send_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.receive_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.receive_panel.Hide()

        receive_sizer = wx.BoxSizer(wx.VERTICAL)

        topbar_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.recv_button = wx.Button(self.receive_panel, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0)
        topbar_sizer.Add(self.recv_button, 0, wx.ALL, 5)

        self.recv_title = wx.StaticText(self.receive_panel, wx.ID_ANY, u"File(s) Available To Download",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.recv_title.Wrap(-1)
        topbar_sizer.Add(self.recv_title, 0, wx.ALIGN_CENTER | wx.LEFT, 100)

        receive_sizer.Add(topbar_sizer, 0, wx.EXPAND, 5)

        file_name_list_choices = []
        self.file_name_list = wx.ListBox(self.receive_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                         file_name_list_choices, wx.LB_NEEDED_SB | wx.LB_SINGLE)
        receive_sizer.Add(self.file_name_list, 1, wx.ALL | wx.EXPAND, 25)

        self.receive_panel.SetSizer(receive_sizer)
        self.receive_panel.Layout()
        receive_sizer.Fit(self.receive_panel)
        main_sizer.Add(self.receive_panel, 1, wx.EXPAND | wx.ALL, 5)

        frame_sizer.Add(main_sizer, 1, wx.EXPAND, 0)

        self.SetSizer(frame_sizer)
        self.Layout()
        self.main_menubar = wx.MenuBar(0)
        self.main_menu = wx.Menu()
        self.switch_panels = wx.MenuItem(self.main_menu, wx.ID_ANY, u"Switch Panels" + u"\t" + u"CTRL+s",
                                         wx.EmptyString, wx.ITEM_NORMAL)
        self.main_menu.Append(self.switch_panels)

        self.main_menu.AppendSeparator()

        self.exit_menu = wx.MenuItem(self.main_menu, wx.ID_ANY, u"Exit" + u"\t" + u"CTRL+q", wx.EmptyString,
                                     wx.ITEM_NORMAL)
        self.main_menu.Append(self.exit_menu)

        self.main_menubar.Append(self.main_menu, u"Main")

        self.file_menu = wx.Menu()
        self.send_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, u"Send" + u"\t" + u"SHIFT+s", wx.EmptyString,
                                          wx.ITEM_NORMAL)
        self.file_menu.Append(self.send_menu_item)

        self.recv_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, u"Recv" + u"\t" + u"SHIFT+r", wx.EmptyString,
                                          wx.ITEM_NORMAL)
        self.file_menu.Append(self.recv_menu_item)

        self.main_menubar.Append(self.file_menu, u"File")

        self.SetMenuBar(self.main_menubar)

        self.Centre(wx.BOTH)

        # Connect Events
        self.recv_button.Bind(wx.EVT_BUTTON, self.refresh)
        self.file_name_list.Bind(wx.EVT_LISTBOX_DCLICK, self.recv_file)
        self.Bind(wx.EVT_MENU, self.handle_panel_switch, id=self.switch_panels.GetId())
        self.Bind(wx.EVT_MENU, self.handle_exit, id=self.exit_menu.GetId())
        self.Bind(wx.EVT_MENU, self.handle_send_browse, id=self.send_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.handle_recv_browse, id=self.recv_menu_item.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def refresh(self, event=None):
        file_names = CLIENT.get_file_list()
        self.file_name_list.Clear()
        for file_name in file_names:
            self.file_name_list.Insert(file_name, 0)
        self.Layout()

    def recv_file(self, event):
        filename = event.GetString()
        if filename:
            wx.MessageBox(CLIENT.recv_files(filename))

    def handle_panel_switch(self, event):
        if self.send_panel.IsShown():
            self.send_panel.Hide()
            self.refresh()
            self.receive_panel.Show()
        else:
            self.receive_panel.Hide()
            self.send_panel.Show()
        self.Layout()

    def handle_exit(self, event):
        self.Close(True)

    def handle_send_browse(self, event):
        SendDialog(self).ShowModal()

    def handle_recv_browse(self, event):
        RecvDialog(self).ShowModal()


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, textCtrl):
        wx.FileDropTarget.__init__(self)
        self.textCtrl = textCtrl

    def OnDropFiles(self, x, y, file_names):
        """
        When files are dropped, write where they were dropped and then the file paths themselves
        """
        self.textCtrl.AppendText("\n{} file(s) dropped. Sending...\n".format(len(file_names)))
        text = ""
        for file_path in file_names:
            try:
                self.textCtrl.AppendText(file_path + '\n')
                print(file_path)
                if file_path == file_names[-1]:
                    text = CLIENT.send_file(file_path, True)
                else:
                    text = CLIENT.send_file(file_path, False)
            except Exception as err:
                print(str(err))
        self.textCtrl.AppendText("\n" + text + "\n")
        return True


class RecvDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                           size=wx.Size(585, 183), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        _recv_sizer = wx.BoxSizer(wx.VERTICAL)

        recv_sizer = wx.BoxSizer(wx.VERTICAL)

        recv_choice_choices = CLIENT.get_file_list()
        self.recv_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, recv_choice_choices, 0)
        self.recv_choice.SetSelection(0)
        recv_sizer.Add(self.recv_choice, 0, wx.ALL | wx.EXPAND, 15)

        recv_browser_buttons = wx.StdDialogButtonSizer()
        self.recv_browser_buttons_ok = wx.Button(self, wx.ID_OK)
        recv_browser_buttons.AddButton(self.recv_browser_buttons_ok)
        self.recv_browser_buttons_cancel = wx.Button(self, wx.ID_CANCEL)
        recv_browser_buttons.AddButton(self.recv_browser_buttons_cancel)
        recv_browser_buttons.Realize()

        recv_sizer.Add(recv_browser_buttons, 1, wx.ALIGN_CENTER, 5)

        _recv_sizer.Add(recv_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(_recv_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.recv_browser_buttons_cancel.Bind(wx.EVT_BUTTON, self.kill_recv_dialog)
        self.recv_browser_buttons_ok.Bind(wx.EVT_BUTTON, self.handle_recv_file_browser)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def kill_recv_dialog(self, event):
        self.Destroy()

    def handle_recv_file_browser(self, event):
        file_name = self.recv_choice.GetStringSelection()
        wx.MessageBox(CLIENT.recv_files(file_name))
        self.Destroy()


class SendDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                           size=wx.Size(585, 183), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        _send_sizer = wx.BoxSizer(wx.VERTICAL)

        send_sizer = wx.BoxSizer(wx.VERTICAL)

        self.send_browser = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition,
                                              wx.DefaultSize, wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST)
        send_sizer.Add(self.send_browser, 0, wx.ALL | wx.EXPAND, 10)

        send_browser_buttons = wx.StdDialogButtonSizer()
        self.send_browser_buttons_ok = wx.Button(self, wx.ID_OK)
        send_browser_buttons.AddButton(self.send_browser_buttons_ok)
        self.send_browser_buttons_cancel = wx.Button(self, wx.ID_CANCEL)
        send_browser_buttons.AddButton(self.send_browser_buttons_cancel)
        send_browser_buttons.Realize()

        send_sizer.Add(send_browser_buttons, 1, wx.ALIGN_CENTER, 5)

        _send_sizer.Add(send_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(_send_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.send_browser_buttons_cancel.Bind(wx.EVT_BUTTON, self.kill_send_dialog)
        self.send_browser_buttons_ok.Bind(wx.EVT_BUTTON, self.handle_send_file_browser)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def kill_send_dialog(self, event):
        self.Destroy()

    def handle_send_file_browser(self, event):
        path = self.send_browser.GetPath()
        while not path or os.path.isfile(path):
            wx.MessageBox("Please choose a valid path")
            path = self.send_browser.GetPath()
        wx.MessageBox(CLIENT.send_file(path, True))
        self.Destroy()


class LoginDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Lgoin", pos=wx.DefaultPosition, size=wx.Size(642, 227),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        _login_sizer = wx.BoxSizer(wx.VERTICAL)

        username_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.username_text = wx.StaticText(self, wx.ID_ANY, u"Username:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.username_text.Wrap(-1)
        username_sizer.Add(self.username_text, 0, wx.ALL, 5)

        self.login_username = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        username_sizer.Add(self.login_username, 1, wx.ALL, 5)

        _login_sizer.Add(username_sizer, 1, wx.EXPAND | wx.RIGHT, 20)

        password_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.password_text = wx.StaticText(self, wx.ID_ANY, u"Password: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.password_text.Wrap(-1)
        password_sizer.Add(self.password_text, 0, wx.ALL, 5)

        self.login_password = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                          wx.TE_NOHIDESEL | wx.TE_PASSWORD)
        password_sizer.Add(self.login_password, 1, wx.ALL, 5)

        _login_sizer.Add(password_sizer, 1, wx.EXPAND | wx.RIGHT, 20)

        self.login_status = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.login_status.Wrap(-1)
        self.login_status.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString))
        self.login_status.SetForegroundColour(wx.Colour(255, 0, 0))
        self.login_status.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.login_status.Hide()

        _login_sizer.Add(self.login_status, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        login_button_sizer = wx.StdDialogButtonSizer()
        self.login_button_sizerOK = wx.Button(self, wx.ID_OK)
        login_button_sizer.AddButton(self.login_button_sizerOK)
        login_button_sizer.Realize()

        _login_sizer.Add(login_button_sizer, 5, wx.ALIGN_CENTER, 5)

        self.SetSizer(_login_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.login_button_sizerOK.Bind(wx.EVT_BUTTON, self.handle_auth)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def handle_auth(self, event):
        global CLIENT
        if not CLIENT:
            CLIENT = Client()
        username = self.login_username.GetValue()
        password = self.login_password.GetValue()
        if not username or not password:
            self.login_status.SetLabelText("Please Enter Your Credentials")
            self.login_status.Show()
            self.Layout()
        else:
            authenticated = CLIENT.login(username, password)
            if authenticated:
                self.Destroy()
            else:
                self.login_status.SetLabelText("Wrong Credentials try again")
                self.login_status.Show()
                self.Layout()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(None)
    frame.Show()
    LoginDialog(frame).ShowModal()
    app.MainLoop()
    CLIENT.socket.close()
