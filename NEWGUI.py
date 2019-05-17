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

        self.send_title = wx.StaticText(self.send_panel, wx.ID_ANY, u"Drug Here o Send File(s)", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.send_title.Wrap(-1)
        send_sizer.Add(self.send_title, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.send_file_text = wx.TextCtrl(self.send_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                          wx.DefaultSize, wx.TE_MULTILINE | wx.TE_READONLY)
        send_sizer.Add(self.send_file_text, 1, wx.ALL | wx.EXPAND, 5)

        self.send_panel.SetSizer(send_sizer)
        self.send_panel.Layout()
        send_sizer.Fit(self.send_panel)
        main_sizer.Add(self.send_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.receive_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.receive_panel.Hide()

        recieve_sizer = wx.BoxSizer(wx.VERTICAL)

        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        self.recv_button = wx.Button(self.receive_panel, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer5.Add(self.recv_button, 0, wx.ALL, 5)

        self.recv_title = wx.StaticText(self.receive_panel, wx.ID_ANY, u"File(s) Available To Download",
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.recv_title.Wrap(-1)
        bSizer5.Add(self.recv_title, 0, wx.ALIGN_CENTER | wx.LEFT, 100)

        recieve_sizer.Add(bSizer5, 0, wx.EXPAND, 5)

        file_name_listChoices = []
        self.file_name_list = wx.ListBox(self.receive_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                         file_name_listChoices, wx.LB_NEEDED_SB | wx.LB_SINGLE)
        recieve_sizer.Add(self.file_name_list, 1, wx.ALL | wx.EXPAND, 5)

        self.receive_panel.SetSizer(recieve_sizer)
        self.receive_panel.Layout()
        recieve_sizer.Fit(self.receive_panel)
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
        self.Bind(wx.EVT_MENU, self.handle_send_browes, id=self.send_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.handle_recv_browes, id=self.recv_menu_item.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def refresh(self, event):
        event.Skip()

    def recv_file(self, event):
        event.Skip()

    def handle_panel_switch(self, event):
        if self.send_panel.IsShown():
            self.send_panel.Hide()
            self.receive_panel.Show()
        else:
            self.receive_panel.Hide()
            self.send_panel.Show()
        self.Layout()

    def handle_exit(self, event):
        self.Close(True)

    def handle_send_browes(self, event):
        SendDialog(self).ShowModal()

    def handle_recv_browes(self, event):
        RecvDialog(self).ShowModal()


class RecvDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                           size=wx.Size(585, 183), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        _recv_sizer = wx.BoxSizer(wx.VERTICAL)

        recv_sizer = wx.BoxSizer(wx.VERTICAL)

        recv_choiceChoices = CLIENT.get_file_list()
        self.recv_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, recv_choiceChoices, 0)
        self.recv_choice.SetSelection(0)
        recv_sizer.Add(self.recv_choice, 0, wx.ALL | wx.EXPAND, 15)

        recv_browser_burrons = wx.StdDialogButtonSizer()
        self.recv_browser_burronsOK = wx.Button(self, wx.ID_OK)
        recv_browser_burrons.AddButton(self.recv_browser_burronsOK)
        self.recv_browser_burronsCancel = wx.Button(self, wx.ID_CANCEL)
        recv_browser_burrons.AddButton(self.recv_browser_burronsCancel)
        recv_browser_burrons.Realize()

        recv_sizer.Add(recv_browser_burrons, 1, wx.ALIGN_CENTER, 5)

        _recv_sizer.Add(recv_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(_recv_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.recv_browser_burronsCancel.Bind(wx.EVT_BUTTON, self.kill_recv_dialog)
        self.recv_browser_burronsOK.Bind(wx.EVT_BUTTON, self.handle_recv_file_browser)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def kill_recv_dialog(self, event):
        self.Destroy()

    def handle_recv_file_browser(self, event):
        file_name = event.GetString()
        print("filename", file_name)
        print("selection:", event.GetSelection())
        print("data", event.GetClientData())
        print("long", event.GetExtraLong())
        #wx.MessageBox(CLIENT.recv_files(file_name))
        #self.Destroy()


class SendDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                           size=wx.Size(585, 183), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        _send_sizer = wx.BoxSizer(wx.VERTICAL)

        send_sizer = wx.BoxSizer(wx.VERTICAL)

        self.send_browser = wx.DirPickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition,
                                             wx.DefaultSize, wx.DIRP_DEFAULT_STYLE | wx.DIRP_DIR_MUST_EXIST)
        send_sizer.Add(self.send_browser, 0, wx.ALL | wx.EXPAND, 10)

        send_browser_burrons = wx.StdDialogButtonSizer()
        self.send_browser_burronsOK = wx.Button(self, wx.ID_OK)
        send_browser_burrons.AddButton(self.send_browser_burronsOK)
        self.send_browser_burronsCancel = wx.Button(self, wx.ID_CANCEL)
        send_browser_burrons.AddButton(self.send_browser_burronsCancel)
        send_browser_burrons.Realize();

        send_sizer.Add(send_browser_burrons, 1, wx.ALIGN_CENTER, 5)

        _send_sizer.Add(send_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(_send_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.send_browser_burronsCancel.Bind(wx.EVT_BUTTON, self.kill_send_dialog)
        self.send_browser_burronsOK.Bind(wx.EVT_BUTTON, self.handle_send_file_browser)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def kill_send_dialog(self, event):
        event.Skip()

    def handle_send_file_browser(self, event):
        event.Skip()


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
        login_button_sizer.Realize();

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
            groups = CLIENT.login(username, password)
            if groups:
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
