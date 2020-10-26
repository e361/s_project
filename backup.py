from kademlia.kad import DHT
from kademlia.hashing import random_id
from art import *

from essential import User

import socket
import json
import time

host = "localhost"
port = 9000
nodeInfo = ("localhost", 9002, random_id())

class Chatroom():
    def __init__(self):
        self.username = None
        self.bootPeer = None
        data = self.readConfigFile()

        print("登入中... 尋找是否有帳戶資料...")
        time.sleep(1)
        if not data:
            mov = self.intro()
        else:
            self.username = data[0]
            print("已經有節點id 和 username")
            print("username: %s , id: %s" % (data[0], data[1]))
        self.join()
         
    def readConfigFile(self, f=None):
        with open("login2.txt", 'r') as f:
            tmp =  f.readlines()
        if not tmp:
            return None
        else:
            tmp = list(map(lambda x : x.strip('\n'), tmp))
            return tmp

    def __callBootServer(self, request):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect( (host, port) )
                sock.sendall(request.encode("ascii"))
                response = str(sock.recv(1024), "ascii")
                print("Received: {}\n".format(response) )
                return response

        except OSError as e:
            print("registry process failed, please try again")

    def intro(self):
        tfont = "standard"
        tprint("Welcome to P2Pchat, tfont")
        time.sleep(1)
        tprint("Please enter your username:", tfont)
        self.username = input()
        
        print("join the kad network? ")
        mov = input()
        return mov

    def join(self):
        print("\n對 BootServer 傳送 join 命令...")
        nodeId = random_id()
        localPort = 9001
        request = json.dumps({"user_name" : self.username, "message_type" : "join", "peer_info" : (host, localPort, nodeId) })
        response = self.__callBootServer(request).strip("[']").split(',')
        if 'join' not in response[0]:
            self.bootPeer = (response[0].strip("'"), int(response[1]), int(response[2]))
            print("回傳的啟動節點: ",  self.bootPeer)
    
    def offline(self):
        print("對 BootServer 傳送 offline 命令...")
        request = json.dumps({"user_name" : self.username, "message_type" : "offline", "peer_info" : nodeInfo}) 
        self.__callBootServer(request)

    def probe(self):
        pass

    def retrieve(self):
        pass


if __name__ == "__main__":
    chat = Chatroom()

    if chat.bootPeer:
        local = DHT(host = nodeInfo[0], port = nodeInfo[1], id = nodeInfo[2], seeds = [chat.bootPeer], info = chat.username)
    else:
        local = DHT(host = nodeInfo[0], port = nodeInfo[1], id = nodeInfo[2], info = chat.username)

    print("目前的鄰近節點有: ")
    print(local.peers())
    user = User(local)
    user.createRoom()
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    chat.offline()
