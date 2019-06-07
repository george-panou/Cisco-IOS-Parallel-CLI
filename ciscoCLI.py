#!/usr/bin/python
import wx, wx.html
import sys
import functions
import threading

global hosts
global output
global outputwindow
global app
global commandType

from multiprocessing.pool import ThreadPool
logging=True

aboutText = """<p>This is a programm to run ios commands simultaneously on multiple cisco devices.<p>It uses multithreading to speed up the procedure, opening one parallel SSH connection per host IP 
<p>Add the host IPs on the left panel and the set of commands to be executed on the right panel.<p>The list needs to be consisted of one IP per line 
<p>You can use the formating function to remove illegal characters from the IP list, it will also delete illegal IPs and remove Duplicate IPs.<p>You can check if the IP list contains illegal IPs using the check IPs Button<p> This instance is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b> and uses paramiko,netmiko,telnetlib and wx libraries for the user interface."""

def readHostsFromFile(filename):
   #hosts = [line.rstrip('\r\n') for line in open(filename)]
   f = open(filename, "r")
   return f.read()
    #return hosts

def getResult(thread):

    message = thread.join()
    output.SetValue(message)
    print("Done!")
    print(message)
    return message

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600, 400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())


class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Parallel Cisco CLI",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER |
                                 wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(750, 700))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth() + 25, irep.GetHeight() + 10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class RedirectText:
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        #self.out.WriteText(string)
        wx.CallAfter(self.out.WriteText, string)

class Frame(wx.Frame):
    ipList=None
    def __init__(self, title):

        wx.Frame.__init__(self, None, title=title, pos=(50, 20), size=(1000, 750))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        #Left Box Stuff
        leftBox = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=0, vgap=0)


        #sizer=wx.Sizer()
        #sizer.Add(grid, 1, wx.EXPAND | wx.ALL)

        #hSizer = wx.BoxSizer(wx.HORIZONTAL)

        grid.Add(leftBox, pos=(0, 0))

        ipListLabel = wx.StaticText(panel, -1, "IP List\n(Enter 1 IP per line)")
        ipListLabel.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        leftBox.Add(ipListLabel, 0, wx.ALL, 10)

        self.ipList=wx.TextCtrl(panel, size=(210, 400), style=wx.TE_MULTILINE | wx.HSCROLL,value="")#172.16.10.181\n172.16.10.96")
        #self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onClearList)
        leftBox.Add(self.ipList, 0, wx.ALL, 10)


        formatList = wx.Button(panel, wx.wxEVT_BUTTON, "Format")
        formatList.Bind(wx.EVT_BUTTON, self.OnFormat)
        leftBox.Add(formatList, 0, wx.ALL, 10)

        checkList = wx.Button(panel, wx.wxEVT_BUTTON, "Check")
        checkList.Bind(wx.EVT_BUTTON, self.OnListCheck)
        leftBox.Add(checkList, 0, wx.ALL, 10)

        browse = wx.Button(panel, wx.wxEVT_BUTTON, "Browse for file")
        browse.Bind(wx.EVT_BUTTON, self.OnBrowseForFile)
        leftBox.Add(browse, 0, wx.ALL, 10)

        self.openFileDialog = wx.FileDialog(panel, "Open", "", "",
                                            #"Txt/CSV files (*.txt)|*.txt (*.csv)|*.csv (*.*)|*.* ",
                                            "",
                                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)


        #Rigth Box Stuff
        middleBox = wx.BoxSizer(wx.VERTICAL)
        middleBoxUpper = wx.BoxSizer(wx.VERTICAL)
        grid2 = wx.GridBagSizer(hgap=0, vgap=0)

        grid.Add(grid2,pos=(0,1))#,span=(1,2))



        self.commandListLabel = wx.StaticText(panel, -1, "List of commands\n(Only show commands \nEnter 1 command per line)")
        self.commandListLabel.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        middleBoxUpper.Add(self.commandListLabel, 0, wx.ALL, 10)


        sampleList = ["Config","Show"]

        self.cb = wx.ComboBox(panel,size=wx.DefaultSize,choices=sampleList)
        self.cb.SetSelection(1)
        global commandType
        commandType=1
        middleBoxUpper.Add(self.cb, 0, wx.ALL, 10)
        self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)


        self.commandList = wx.TextCtrl(panel, size=(350, 130), style=wx.TE_MULTILINE|wx.HSCROLL,value="")
        middleBoxUpper.Add(self.commandList, 0, wx.ALL, 10)

        rightBox = wx.BoxSizer(wx.VERTICAL)

       # grid2.Add(rightBox, pos=(0, 2))


        commandListLabel = wx.StaticText(panel, -1, "Credentials")
        commandListLabel.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        rightBox.Add(commandListLabel, 0, wx.ALL, 10)

        usernameLabel = wx.StaticText(panel, -1, "Username")
        rightBox.Add(usernameLabel, 0, wx.ALL, 10)

        self.username = wx.TextCtrl(panel, value="", size=(150, -1))
        rightBox.Add(self.username, 0, wx.ALL, 10)

        passwordLabel = wx.StaticText(panel, -1, "Password")
        rightBox.Add(passwordLabel, 0, wx.ALL, 10)

        self.password = wx.TextCtrl(panel, value="", size=(150, -1),style=wx.TE_PASSWORD)
        rightBox.Add(self.password , 0, wx.ALL, 10)

        creds2Box = wx.BoxSizer(wx.VERTICAL)
        commandListLabel2 = wx.StaticText(panel, -1, "Alternative Creds")
        commandListLabel2.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        creds2Box.Add(commandListLabel2, 0, wx.ALL, 10)

        usernameLabel2 = wx.StaticText(panel, -1, "Username")
        creds2Box.Add(usernameLabel2, 0, wx.ALL, 10)

        self.username2 = wx.TextCtrl(panel, value="", size=(150, -1))
        creds2Box.Add(self.username2, 0, wx.ALL, 10)

        passwordLabel2 = wx.StaticText(panel, -1, "Password")
        creds2Box.Add(passwordLabel2, 0, wx.ALL, 10)

        self.password2 = wx.TextCtrl(panel, value="", size=(150, -1), style=wx.TE_PASSWORD)
        creds2Box.Add(self.password2, 0, wx.ALL, 10)


        #bottomBox = wx.BoxSizer(wx.VERTICAL)
        #grid.Add(bottomBox, pos=(2, 2))


        run = wx.Button(panel, wx.wxEVT_BUTTON, "Run Commands")
        run.Bind(wx.EVT_BUTTON, self.onRunCommands)
        rightBox.Add(run, 0, wx.ALL, 10)


        panel.SetSizer(grid)
        panel.Layout()

        #Logging
        grid3= wx.GridBagSizer(hgap=0, vgap=0)
        grid4 = wx.GridBagSizer(hgap=0, vgap=0)

        grid2.Add(grid3, pos=(0, 1))  # ,span=(1,2))

        log = wx.TextCtrl(panel, wx.ID_ANY, size=(650, 350),
                         style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        middleBox.Add(log, 0, wx.ALL, 10)
        #
        grid3.Add(middleBoxUpper, pos=(0, 0))
        grid3.Add(rightBox, pos=(0, 1))
        grid3.Add(creds2Box, pos=(0, 2))
        grid4.Add(middleBox, pos=(1, 0))
        grid2.Add(grid4, pos=(1, 1))  # ,span=(1,2))
        redir = RedirectText(log)
        sys.stdout = redir


    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()



        if result == wx.ID_OK:
            self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def onClearList(self,event):
        self.ipList.value = ""

    def OnFormat(self, event):
        global hosts
        #print (self.ipList.GetValue())
        ipListText=self.ipList.GetValue()
        hosts=ipListText.splitlines()
        hosts=functions.formatInput(hosts)


        #print(hosts)
        tmpSTR=""
        for host in hosts:
            tmpSTR+=str(host)+"\r\n"
        self.ipList.SetValue(tmpSTR)
        #formatInput(hosts)

    def OnListCheck(self, event):
        global hosts
        # print (self.ipList.GetValue())
        ipListText = self.ipList.GetValue()
        hosts = ipListText.splitlines()
        check = functions.checkIPs(hosts)
        # print(hosts)
        if check and len(hosts)!= 0 :
            print("List seems OK")
        else :
            print("There are errors in the IP list")

    # run the commands on the host list
    def onRunCommands(self,event):
        global hosts
        global app

       #if logging :
       #    app.RedirectStdio()
       #else :
       #    app.RestoreStdio()

        ipListText = self.ipList.GetValue()
        commands=self.commandList.GetValue()
        hosts = ipListText.splitlines()
        print("####################################################################################################")
        print("Starting a new run")
        check = functions.checkIPs(hosts)
        # print(hosts)

        if check and len(hosts) != 0:
            print("List seems OK")
            if len(hosts) != 0:
                global async_result
                global commandType
                #start a different thread than UI in order not to freeze interaction
                async_result=threading.Thread(target=functions.mainLogic, args=(hosts, commands, self.username.GetValue(), self.password.GetValue(),commandType,self.username2.GetValue(),self.password2.GetValue()))
                async_result.start()

            else:
                print("No hosts specified")

        else:
            print("There are errors in the IP list")
            print("Check it or try formating it to auto fix")

    #open file function
    def OnBrowseForFile(self,event):
        self.openFileDialog.ShowModal()
        path=self.openFileDialog.GetPath()

        readHostsFromFile(path)
        self.ipList.SetValue(readHostsFromFile(path))
       # self.openFileDialog.Destroy()

    def OnSelect(self, event):
        obj = self.cb.GetSelection()
        global commandType
        if obj == 0:
            self.commandListLabel.SetLabelText("List of commands\n(Enabled and in config mode \nEnter 1 command per line)")
            commandType=0
        else:
            self.commandListLabel.SetLabelText("List of commands\n(Only show commands \nEnter 1 command per line)")
            commandType=1


if __name__ == "__main__":

    app = wx.App(redirect=False)  # Error messages go to popup window

    top = Frame("Multiple Cisco Devices CLI Controller")
    top.Show()
    app.MainLoop()
