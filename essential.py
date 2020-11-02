import socket
import socketserver
import uuid
import json

class MouthPiece():
    def send(self, host, port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect( (host, port))
            sock.sendall(message.encode('ascii'))

class MessageTable():
    def template():
        messageFormat = None

""" 
    Implementation of user's mechanism for chat room, include
        - createRoom
        - invite
        - leave
        - sendmessage
"""

class User(MouthPiece):
    def __init__(self):
        self.switch = True

    # receive a dht local node,
    # new a roomId, and record it at dht peer's roomInfo.
    def createRoom(self, rpc):
        roomId = uuid.uuid4()
        print("創造新的群組... ", roomId)
        userName = rpc.peer.info
        toUpdateRoomInfo = rpc.peer.roomInfo
        newRoomRecord = {roomId : userName}

        toUpdateRoomInfo.update(newRoomRecord)
        print("新增到群組列表... %s " % toUpdateRoomInfo)

    def invite(self, targer, roomId, rpc):
        pass

    def leave(self, roomId, rpc):
        pass

    def sendMessage(self, message, target, rpc):
        target.ping(socket = rpc.server.socket,
                    peer_id = rpc.peer.id,
                    peer_info = rpc.peer.info)
        send(target[0], target[1], message)



"""
    Implementaiont of socket which handle transmission of external message.
"""

class handler(socketserver.BaseRequestHandler):
    def handle(self):
       pass 




