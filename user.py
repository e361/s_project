import socketserver
import socket
import threading
import uuid
import time
import json

class MouthPiece():
    def send(self, host, port, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect( (host, port))
                sock.sendall(message.encode('ascii'))
                response = str(sock.recv(1024), "ascii")
            return response
        except Exception:
            print("Oops 對方不在, 聊天室處理中~")
            if message['message_type'] == 'join' or message['message_type'] == 'offline':
                return
            with open('backup.txt', 'a') as f:
                message = json.loads(message)
                message.update({"host": host})
                f.write(json.dumps(message) + '\n')

    def dumpMessage(self, command, kwargs):
        request = dict({"message_type": command}, **kwargs)
        return json.dumps(request)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        packet = json.loads(self.request.recv(1024))
        if packet["message_type"] == 'sendmessage':
            if packet['roomId']:
                print(packet['time'], packet['roomId'], packet['user_name'], packet['content'], sep=', ')
            else:
                print(packet['time'], packet['user_name'],packet['content'], sep = ", ")
            with open('history.txt', 'a') as f:
                f.write("{},{},{},{}".format(packet['time'], packet['roomId'], packet['user_name'], packet['content']))
                
        if packet["message_type"] == 'invite':
            roomId = packet['roomId']
            username = packet['roomMember']
            self.server.addRoom({roomId: username})

        if packet["message_type"] == 'leave':
            roomId = packet['roomId'] 
            username = packet['user_name']
            member = self.server.room[roomId]
            member.remove(username)

        if packet["message_type"] == "retrieve":
            response = [] 
            new = []
            ip = packet['host']
            print("開始獲取離線檔案")
            with open('backup.txt', 'r+') as f:
                response = f.readlines()

            for item in response:
                tmp = json.loads(item)
                if tmp['host'] == packet['host']:
                    if tmp['message_type'] == 'invite':
                        self.server.send(tmp['host'], 9002, item)
                    elif tmp['message_type'] == 'leave':
                        self.server.send(tmp['host'], 9002, item)
                    elif tmp['message_type'] == 'sendmessage':
                        roomId = tmp['roomId']
                        self.server.send(tmp['host'], 9002, item)

            for item in response:
                tmp = json.loads(item)
                if tmp['host'] != packet['host']:
                    new.append(item)

            with open('backup.txt', 'w') as f:
                for item in new:
                    f.write(item)
            print(response)

""" 
    Implementation of user's mechanism for chat room
        - createRoom
        - invite
        - leave
        - sendmessage
"""

class User(socketserver.ThreadingMixIn, socketserver.TCPServer, MouthPiece):

    def __init__(self, handler, rpc):
        self.server = socketserver.TCPServer.__init__(self, ("localhost", 9002), handler)
        self.room = rpc.peer.roomInfo
        self.connPort = 9002
        self.username = rpc.peer.info
        t = threading.Thread(target = self.serve_forever, daemon = True)
        t.start()
        self.roomUpdate()


    def roomUpdate(self):
        with open('group.txt', 'r') as f:
            tmp = f.readlines()
        for record in tmp:
            record = json.loads(record)
            self.room.update(record)
    """ 
        new a roomId, and record it in kademlia peer's roomInfo.
    """
    def createRoom(self):
        roomId = str(uuid.uuid4())[:8]
        print("創造新的群組... ", roomId)
        self.room.update({roomId: [self.username]})

    def invite(self, targets, roomId):
        message = self.dumpMessage("invite", {"user_name": self.username, "roomId": roomId, "roomMember": list(self.room[roomId])} )
        for user in targets:
            self.send(user, 9002, message)

    def leave(self, targets, roomId):
        message = self.dumpMessage("leave", {"user_name": self.username, "roomId": roomId})
        self.room[roomId].remove(self.username)
        for user in targets: 
            self.send(user, 9002, message)
        self.delRoom(roomId)
       
    def sendMessage(self, targets, message, roomId=None):
        now = time.ctime(time.time())
        packet = {"time": now, "roomId": roomId, "user_name": self.username, "content": message+'\n'}
        packet = self.dumpMessage("sendmessage", packet)
        for user in targets:
            self.send(user, 9002, packet)

    def delRoom(self, roomId):
        del self.room[roomId] 

    def addRoom(self, record):
        self.room.update(record)

    def iterUsers(self, chatroom, roomId):
        return [chatroom.network[x] for x in self.room[roomId] if x != chatroom.username]
