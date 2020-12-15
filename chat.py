from kademlia.kad import DHT
from kademlia.hashing import random_id
from user import User, MouthPiece, Handler

import threading
import time
import json

class Chatroom(MouthPiece):
    """ 
        host, port := ip and port of kademlia.
        peerId     := id of kademlia.
        bootPeer   := one of others kademlia peer online.
        bootServer := the ip and port of the tracker.
    """
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 9001
        self.peerId = None
        self.bootPeer = None
        self.bootServer = ("localhost", 9000)
        self.network = dict()

        loginData = self.readLoginFile()
        print("登入中... 尋找是否有帳戶資料...\n")
        if not loginData:
            self.login()
        else:
            self.username, self.peerId = loginData
            self.peerId = int(self.peerId)
            print("已經有節點id 和 username")
            print("username: %s , id: %s" % (self.username, self.peerId))
        self.join()
         
    def login(self):
        print("Welcome to P2Pchat ")
        self.username = input("Please enter your username: ")
        with  open("login.txt", 'w') as f:
            f.write("{}\n".format(self.username))
            self.peerId = random_id()
            f.write(str(self.peerId))
        print("join into the kad network... ")
    
    def readLoginFile(self):
        with open("login.txt", 'r') as f:
            tmp = f.readlines()
            tmp = list(map(lambda x : x.strip('\n'), tmp))
        return tmp

    def join(self):
        print("\n對 BootServer 傳送 join 命令...")
        request = self.dumpMessage("join", {"user_name": self.username, "peer_info": (self.host, self.port, self.peerId)})
        try:
            response = self.send(self.bootServer[0], self.bootServer[1], request)
            response = response.strip("[']").split(',')

            # tracker response for no seed!
            if 'join' not in response[0]:
                self.bootPeer = (response[0].strip("'"), int(response[1]), int(response[2]))
                print("回傳的啟動節點: ",  self.bootPeer)

        except Exception as e:
            print("Theres something problem, {}".format(e))
    
    def offline(self, user):
        print("\n對 BootServer 傳送 offline 命令...")
        request = self.dumpMessage("offline", {"user_name" : self.username, "peer_info" : (self.host, self.port, self.peerId)}) 

        # receive an "ok" from bootServer
        ok = self.send(self.bootServer[0], self.bootServer[1], request)
        print(ok)
        if user.room:
            with open('group.txt', 'w') as f:
                f.write(json.dumps(user.room))
    def probe(self, rpc, user):
        for u in rpc.peers():
            key = u['info']
            value = u['host']
            self.network.update({key: value})

    def retrieve(self, user):
        message = self.dumpMessage("retrieve", {"username": self.username, "host": self.host})
        for target in self.network:
            response = self.send(self.network[target], 9002, message)
            with open('history.txt', 'a') as f:
                pass
