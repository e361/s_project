from kad import DHT
from art import *
from hashing import random_id
import socket
import json
import uuid
import time

host = "localhost"
port = 9000
nodeInfo = ("localhost", 9001, random_id())

class Chatroom():
    
    def __init__(self):
        self.tip = None
        self.username = None
        self.bootPeer = None
        mov = self.intro()
        self.join()
         
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
        tprint("Please enter your username:", tfont)
        self.username = input()
        
        print("join the kad network? ")
        mov = input()
        return mov

    def join(self):
        print("對 BootServer 傳送 join 命令...")
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

class User():
    def createRoom(self, local):
        roomId = uuid.uuid4()  
        print("創造新的群組...", roomId)
        local.peer.roomInfo.update({roomId : [local.peer.info] })
        print("新增到群組列表... % s \n" % local.peer.roomInfo)

    def invite(self, user, roomId):
        pass

    def leave(self):
        pass

    def sendMessage(self, group=False):
        if not group:
            pass
        pass

if __name__ == "__main__":
    chat = Chatroom()

    if chat.bootPeer:
        local = DHT(host = nodeInfo[0], port = nodeInfo[1], id = nodeInfo[2], seeds = [chat.bootPeer], info = chat.username)
    else:
        local = DHT(host = nodeInfo[0], port = nodeInfo[1], id = nodeInfo[2], info = chat.username)

    print("目前的鄰近節點有: ")
    print(local.peers())
    monitor = User()
    monitor.createRoom(local)
    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            break
    chat.offline()
