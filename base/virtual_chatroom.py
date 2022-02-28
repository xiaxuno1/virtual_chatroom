# --------------------------------------------------
# !/usr/bin/python
# -*- coding: utf-8 -*-
# PN: virtual_chatroom
# FN: virtual_chatroom
# Author: xiaxu
# DATA: 2022/2/28
# Description:虚拟茶话会初次实现
# ---------------------------------------------------
from asyncore import dispatcher
from asynchat import async_chat
import socket
import asyncore

class ChatSession(async_chat):
    """
    处理服务器和客户端数据的类
    """
    def __init__(self,server,sock):
        async_chat.__init__(self,sock)
        self.server = server
        self.data = []  #存放接收数据
        self.set_terminator(b"\r\n") #设置结束符
        self.push(b"welcome to chatroom \r\n")

    def collect_incoming_data(self, data):
        """
        接收数据
        :param data:
        :return:
        """
        self.data.append(data.decode('gbk'))

    def found_terminator(self):
        """
        收到结束符后处理
        :return:
        """
        line = "".join(self.data)
        self.data = [] #接收到结束符后将接受去清空
        print(line)
        self.server.broadcast(line.encode('gbk'))  #将接受到的数据广播到其他的在线用户

    def handle_close(self):
        """
        关闭的相关方法
        :return:
        """
        async_chat.handle_close(self)
        self.server.disconnect(self)

class ChatServer(dispatcher):
    """
    用于建立服务器连接的相关设置
    """
    def __init__(self,port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM) #设置通信协议
        self.set_reuse_addr()  #设置端口重复使用，避免崩溃后无法重启
        self.bind(('',port))
        self.listen(5) #最大监听线程数
        self.sessions = []  #收集sessions

    def disconnect(self,session):
        self.sessions.remove(session)

    def handle_accept(self):
        """
        重写，让其可以接收连接
        :return:
        """
        conn,addr = self.accept() #设置接收客户端，并返回连接断相和地址
        self.sessions.append(ChatSession(self,conn))  #添加会话

    def broadcast(self,line):  #推送给不同会话的用户
        for session in self.sessions:
            session.push(line+b"\r\n")

if __name__ == "__main__":
    PORT = 5005
    s = ChatServer(PORT)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()

