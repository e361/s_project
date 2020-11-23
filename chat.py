from kademlia.kad import DHT
from kademlia.hashing import random_id
from user import User, MouthPiece, Handler

import socket
import json
import time
import user

host = "localhost"
port = 9000
nodeInfo = ("localhost", 9001, random_id())

class Chatroom(MouthPiece):
    def __init__(self):
        self.username = None
        self.bootPeer = None
        data = self.readConfigFile()

        print("登入中... 尋找是否有帳戶資料...\n")
        time.sleep(1)
        if not data:
            self.login()
        else:
            self.username = data[0]
            nodeInfo = ("localhost", 9001, int(data[1]))
            print("已經有節點id 和 username")
            print("username: %s , id: %s" % (data[0], data[1]))
        self.join()
         
    def login(self):
        print("Welcome to P2Pchat ")
        time.sleep(1)
        self.username = input("Please enter your username: ")
        f = open("login.txt", 'w')
        f.write("{}\n".format(self.username))
        f.write(str(random_id()) )
        f.close()
        
        print("join into the kad network... ")
        time.sleep(2)
    
    def readConfigFile(self):
        with open("login.txt", 'r') as f:
            tmp = f.readlines()
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


    def join(self):
        print("\n對 BootServer 傳送 join 命令...")
        nodeId = random_id()
        request = json.dumps({"user_name" : self.username, "message_type" : "join", "peer_info" : nodeInfo})
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
    print(local.peers(), end='\n\n')
    user = User(Handler)
    
    while True:
        try:
            time.sleep(1)
            instruction = input("""選擇功能: \n\t1. 搜尋聊天室用戶 
                    \n\t2. 創造群組
                    \n\t3. 離開群組
                    \n\t4. 聊天
                    \n\t5. 顯示聊天室群組 
                    \n\t6. 邀請 =====> """)

            if(instruction == '1'):
                for users in local.peers():
                    print("線上用戶: {}".format(users['info']))
               
            if(instruction == '2'):
                user.createRoom(local)

            if(instruction == '3'):
                pass
            if(instruction == '4'):
                target = input("想傳給誰??")
                message = input("想傳些什麼??")
                message = {"message_type" : 'sendmessage', "user_name" : local.peer.info, "content" : message}
                user.sendMessage(message, target, local)

            if(instruction == '5'):
                print("群組..... {}".format(local.peer.roomInfo))

            if(instruction == '6'):
                pass
            
        except KeyboardInterrupt:
            break
    chat.offline()
