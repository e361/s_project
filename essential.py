import socketserver
import uuid
import json

""" 
    Implementation of user's mechanism for chat room, include
        - createRoom
        - invite
        - leave
        - sendmessage
"""

class User():
    def __init__(self, local):
        self.rpc = local 

    # receive a dht local node,
    # new a roomId, and record it at dht peer's roomInfo.
    def createRoom(self):
        roomId = uuid.uuid4()
        print("創造新的群組... ", roomId)
        userName = self.rpc.peer.info
        toUpdateRoomInfo = self.rpc.peer.roomInfo
        newRoomRecord = {roomId : userName}

        toUpdateRoomInfo.update(newRoomRecord)
        print("新增到群組列表... %s " % toUpdateRoomInfo)

    def invite(self, targer, roomId):
        pass

    def leave(self, roomId):
        pass

    def sendMessage(self, target):
        pass



"""
    Implementaiont of socket which handle transmission of external message.
"""

class handler(socketserver.BaseRequestHandler):
    def handle(self):
       pass 


class Mouthpiece():
    def send(self):
        pass
