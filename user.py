import socketserver
import socket
import uuid
import json

class MouthPiece():
    def send(self, host, port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect( (host, port))
            sock.sendall(message.encode('ascii'))
            response = str(sock.recv(1024), "ascii")
        return response

    def dumpMessage(self, command, kwargs):
        request = dict({"message_type": command}, **kwargs)
        return json.dumps(request)



class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        packet = json.loads(self.request.recv(1024))

        if packet["message_type"] == 'sendmessage':
            print(packet['content'])
            with open('history.txt', 'a') as f:
                f.write("{}\n".format(packet['content']))
                
        if packet["message_type"] == 'invite':
            roomId = packet['roomId']
            username = packet['roomMember']
            username.append(self.server.username)
            self.server.addRoom({roomId: username})

        if packet["message_type"] == 'leave':
            roomId = packet['roomId'] 
            username = packet['user_name']
            member = self.server.room[roomId]
            member.remove(username)

""" 
    Implementation of user's mechanism for chat room
        - createRoom
        - invite
        - leave
        - sendmessage
    all function need a local kademlia peer target
"""

class User(socketserver.ThreadingMixIn, socketserver.TCPServer, MouthPiece):

    def __init__(self, handler, rpc):
        self.server = socketserver.TCPServer.__init__(self, ("localhost", 9002), handler)
        self.room = rpc.peer.roomInfo
        self.username = rpc.peer.info
        self.port = 9002

    """ 
        new a roomId, and record it in kademlia peer's roomInfo.
    """
    def createRoom(self):
        roomId = uuid.uuid4()
        print("創造新的群組... ", roomId)
        self.room.update({str(roomId): [self.username]})

    def invite(self, target, roomId, rpc):
        self.send(target[0], target[1], self.dumpMessage("invite", message))

    def leave(self, roomId, rpc):
        self.delRoom(rpc, roomId)
        
    def sendMessage(self, message, target, rpc):
        """target.ping(socket = rpc.server.socket,
                    peer_id = rpc.peer.id,
                    peer_info = rpc.peer.info)
        """
        
        #message = json.dumps(message)
        self.send(target[0], target[1], self.dumpMessage("sendmessage", message))

    def delRoom(self, roomId):
        del self.room[roomId] 

    def addRoom(self, record):
        self.room.update(record)
