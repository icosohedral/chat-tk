import time, requests, json, threading
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk

class Chat(object):
    def __init__(self, ts):
        self.timestamp = ts
        self.server = "192.168.0.30"
        return
    
    def handshake(self):
        url = 'http://%s/chatServer?handshake=True' % self.server
        try:
            res = requests.get(url)
            res.raise_for_status()
            return True
        except:
            return False
    
    def getNewMessages(self):
        url = 'http://%s/chatServer?getmessage=%s' % (self.server, self.timestamp)
        res = requests.get(url)
        content = res.text.replace("&#x27;", "\"")
        messages = json.loads(content)
        return messages
        
    def sendMessage(self, username, message):
        url = 'http://192.168.0.30/chatServer?timestamp=%s&username=%s&message=%s' % (self.timestamp, username, message)
        res = requests.get(url)
        if res.text == 'succ':
            return True
        else:
            return False

class GUI(object):
    def __init__(self):
        # main
        self.window = Tk()
        self.window.title("Chat Client")
        self.window.geometry('350x360')
        self.window.resizable(0,0)
        # frame
        self.frm1 = Frame(self.window)
        self.frm2 = Frame(self.window)
        self.frm3 = Frame(self.window)
        # elements in window
        self.initWindow()
    
    def initWindow(self):
        # frame 1 for message area
        self.frm1.config(bg='white', height=186, width=320)
        self.frm1.place(x=20, y=20)
        self.txt = scrolledtext.ScrolledText(self.frm1, height=14, width=43, wrap=WORD)
        self.txt.place(in_=self.frm1)
        # frame 2 for entry
        self.frm2.config(bg='red', height=50, width=300)
        self.frm2.place(x=20, y=230)
        self.entry_content = scrolledtext.ScrolledText(self.frm2, height=15, width=43, wrap=WORD)
        self.entry_content.place(width=320, height=50)
        # frame 3 for username & send button
        self.frm3.config(height=50, width=300)
        self.frm3.place(x=20, y=280)
        self.lb_username = Label(self.frm3, text="用户名:", anchor='w')
        self.lb_username.place(x=0, y=13, width=70)
        self.entry_username = Entry(self.frm3)
        self.entry_username.place(x=55, y=13, width=100, height=25)
        self.btn_send = Button(self.frm3, text='发送', command=self.send)
        self.btn_send.place(x=200, y=10, width=100, height=30)
        # statue bar
        self.statusbar = Label(self.window, text="连接中…", bd=1, relief=SUNKEN, anchor='w')
        self.statusbar.pack(side=BOTTOM, fill=X)
        # check connection
        def connect():
            self.timestamp = time.time()
            self.entryState('DISABLED')
            if Chat(self.timestamp).handshake():
                msg = '连接服务端成功！'
                self.entryState('txt')
            else:
                msg = '连接服务端失败！'
                self.entryState('DISABLED')
            self.statuebar_show(msg)
        bg = threading.Thread(target=connect)
        bg.start()
        # get new message
        messages = []
        def getNewMessage():
            while True:
                len_old = len(messages)
                newMessages = Chat(self.timestamp).getNewMessages()
                for message in newMessages["messages"]:
                    if message not in messages:
                        messages.append(message)
                        date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(message['timestamp'])))
                        username = message['username']
                        message = message['message']
                        self.msginsert('%s    from: %s\n> %s' % (date, username, message))
                time.sleep(3)
        bg_getNew = threading.Thread(target=getNewMessage, daemon=True)
        bg_getNew.setDaemon(True)
        bg_getNew.start()
        # run
        self.window.mainloop()
        
    def entryState(self, state):
        if state == 'NORMAL':
            self.txt.config(state=NORMAL)
            self.entry_content.config(state=NORMAL)
            self.entry_username.config(state=NORMAL)
            self.btn_send.config(state=NORMAL)
        elif state == 'DISABLED':
            self.txt.config(state=DISABLED)
            self.entry_content.config(state=DISABLED)
            self.entry_username.config(state=DISABLED)
            self.btn_send.config(state=DISABLED)
        elif state == 'txt':
            self.txt.config(state=DISABLED)
            self.entry_content.config(state=NORMAL)
            self.entry_username.config(state=NORMAL)
            self.btn_send.config(state=NORMAL)
            
    def statuebar_show(self, msg):
        def show():
            self.statusbar.config(text=msg)
            time.sleep(3)
            self.statusbar.config(text='')
        bg = threading.Thread(target=show)
        bg.start()

    def send(self):
        self.statuebar_show('消息发送中...')
        def send_bg():
            self.entryState('DISABLED')
            timestamp = time.time()
            username = self.entry_username.get()
            message = self.entry_content.get('1.0', END).rstrip()
            if username and message:
                if Chat(timestamp).sendMessage(username, message):
                    msg = "发送成功！"
                else:
                    msg = "发送失败！"
            else:
                msg = "数据缺失！"
            self.statuebar_show(msg)
            self.entryState('txt')
            self.entry_content.delete('1.0','end')
        bg = threading.Thread(target=send_bg)
        bg.start()
        
    def msginsert(self, msg):
        self.txt.config(state=NORMAL)
        self.txt.insert(INSERT, msg+'\n\n')
        self.txt.update()
        self.txt.config(state=DISABLED)

if __name__ == '__main__':
    mainfz = threading.Thread(target=GUI())
    mainfz.start() 