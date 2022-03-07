# --------------------------------------------------
# !/usr/bin/python
# -*- coding: utf-8 -*-
# PN: virtual_chatroom
# FN: virtual_chatroom2
# Author: xiaxu
# DATA: 2022/3/1
# Description:
# ---------------------------------------------------
from asyncore import dispatcher
from asynchat import async_chat
import socket,asyncore


PORT = 5005
NAME = "Virtual_Chatroom"
class CommandHandler:
    """
    命令解析类，类似于cmd.Cmd;用于解析命令对应的方法，没有时默认返回
    """
    def unknow(self,session,cmd):
        """
        命令方法没有发现时的默认操作
        :return:
        """
        session.push(b"I don't know this cmd: %s\r\n"%cmd.encode("utf-8"))

    def handle(self,session,line):
        """
        解析命令的方法
        :param session:会话对象
        :param line: 传入的内容 如：say hello
        :return:
        """
        if line.strip():return
        parts = line.split(" ",1)
        cmd = parts[0] #分离出命令
        method = getattr(self,"do_"+cmd,None)
        try:
            pass
        #调用方法
        except TypeError as e:
            """没有方法时调用默认方法"""
            print(e)
            self.unknow(session,cmd)

class EndSession(Exception):pass

class Room(CommandHandler):
    """关于聊天室的通用方法"""
    def __init__(self,server):
        self.sessions = []
        self.server = server
    def add(self,session):
        """添加会话，用于广播或者其他用途"""
        self.sessions.append(session)

    def remove(self,session):
        """删除其中的会话"""
        self.sessions.remove(session)

    def broadcast(self,line):
        """将内容消息广播给其他用户"""
        for session in self.sessions:
            session.push(line)

    def do_logout(self,session,line):
        """响应退出命令"""
        raise EndSession

class LoginRoom(Room):
    """定义登陆聊天室对象"""
    def add(self,session):
        Room.add(session) #用继承的方法
        #欢迎词
        self.broadcast(b'Welocome to %s\r\n' % self.server.name.encode('utf-8'))

    def unknow(self,session,cmd):
        """重写默认方法，提示登陆"""
        session.push(b"please login\r\nlike:login Tom\r\n")

    def do_login(self,session,line):
        """定义登陆验证相关方法"""
        name = line.strip.encode("utf-8")
        print(name)
        if not name:
            session.push(b'please enter user_name\r\n')
        elif name in self.server.users:
            session.push(b'The name "%s" is taken \r\n' % name)
            session.push(b'Please try again \r\n')
        else:
            # 用户名没问题，因此将其存储到会话中并将用户移到主聊天室
            session.name = name
            session.enter(self.server.main_room)

class LogoutRoom(Room):
    """定义登出聊天室的方法"""
    def add(self,session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass

class ChatRoom(Room):
    """主聊天室的实现"""
    def add(self,session):
        #登陆信息广播给其他人
        self.broadcast(session.name+b"has enter the room\r\n")

    def do_who(self):
        '''显示谁登陆'''
        pass

    def do_look(self):
        '''展示当前登陆的用户'''
        pass

    def do_say(self):
        '''聊天方法'''
        pass

    def do_remove(self):
        """用户离开后删除用户"""
        pass

class ChatSession(async_chat):
    """处理单个用户连接"""
    def __init__(self,server,sock):
        super().__init__(sock)
        self.server = server
        self.set_terminator(b'\r\n') #设置终止符
        self.data = [] #接收数据
        self.name = None
        self.enter(LoginRoom(server)) #首先登陆

    def collect_incoming_data(self, data):
        """接收数据"""
        self.data.append(data.decode('utf-8'))

    def found_terminator(self):
        """终止处理"""
        line = ''.join(self.data) #将接收的数据列表组合成句子
        self.data = []
        """找命令对应的方法"""
        try:
            self.room.handle(self,line)
        except:
            pass

    def enter(self,room):
        """用于登陆成功后进入新的聊天室（主聊天室）,并且从当前聊天室离开"""
        try:
            cur = self.room  #当前所在的聊天室
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room  #移动到下一个聊天室
        self.add(self)  #添加当前用户

class ChatServer(dispatcher):
    """聊天服务器"""
    def __init__(self,port,name):
        super().__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('',port))
        self.name = name
        self.user = {} #存储用户的字典
        self.listen(5)


    def handle_accept(self):
        conn,addr = self.accept()
        pass

if __name__ == '__main__':
    s = ChatSession(PORT,NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()

