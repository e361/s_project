from kademlia.kad import DHT
from kademlia.hashing import random_id
from user import User, MouthPiece, Handler

import threading
import socket
import json
import time
import user

class Chatroom(MouthPiece):
    def __init__(self):
        self.host = "localhost"
        self.port = 9001
        self.peerId = None
        self.bootPeer = None
        self.bootServer = ("localhost", 9000)

        loginData = self.readLoginFile()
        print("登入中... 尋找是否有帳戶資料...\n")
        time.sleep(1)
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
            if 'join' not in response[0]:
                self.bootPeer = (response[0].strip("'"), int(response[1]), int(response[2]))
                print("回傳的啟動節點: ",  self.bootPeer)

        except Exception as e:
            print("Theres something problem, {}".format(e))
    
    def offline(self):
        print("\n對 BootServer 傳送 offline 命令...")
        request = self.dumpMessage("offline", {"user_name" : self.username, "peer_info" : (self.host, self.port, self.peerId)}) 

        # receive an "ok" from bootServer
        ok = self.send(self.bootServer[0], self.bootServer[1], request)
        print(ok)

    def probe(self):
        pass

    def retrieve(self):
        pass


if __name__ == "__main__":
    chat = Chatroom()

    if chat.bootPeer:
        local = DHT(host = chat.host, port = chat.port, id = chat.peerId, seeds = [(chat.bootPeer)], info = chat.username)
    else:
        local = DHT(host = chat.host, port = chat.port, id = chat.peerId, info = chat.username)

    user = User(Handler, local)
    chatDaemon = threading.Thread(target = user.serve_forever, daemon = True)
    chatDaemon.start()

    
    while True:
        try:
            instruction = input("""選擇功能: \n\t1. 搜尋聊天室用戶 
                    \n\t2. 創造群組
                    \n\t3. 離開群組
                    \n\t4. 聊天
                    \n\t5. 顯示聊天室群組 
                    \n\t6. 邀請 ===============\n """)

            if(instruction == '1'):
                for users in local.peers():
                    print("線上用戶: {}, ip: {}".format(users['info'], users['host']))
               
            if(instruction == '2'):
                user.createRoom()

            if(instruction == '3'):
                print(list(local.peer.roomInfo.keys()))
                roomId = input("想要離開的大廳?")
                message = user.dumpMessage("leave", {"user_name": chat.username, "roomId": roomId})
                user.send("localhost",9010, message)
                user.delRoom(roomId)

            if(instruction == '4'):
                target = input("想傳給誰??")
                message = input("想傳些什麼??")
                user.sendMessage({"content": message, "user_name": local.peer.info}, (target, 9010), local) 
                

            if(instruction == '5'):
                print("目前群組..... {}".format(user.room))

            if(instruction == '6'):
                target = input("想邀請誰??")
                print(list(local.peer.roomInfo.keys()))
                roomId = input("大廳名字??")
                message = json.dumps({"message_type" : 'invite', "user_name": user.username, "roomId": roomId, "roomMember": user.room[roomId]})
                user.send(target, 9010, message)
                member = user.room[roomId]
                for u in local.peers():
                    if u['host'] == target:
                        member.append(u['info'])


        except KeyboardInterrupt:
            break
    chat.offline()
