import socketserver
import socket
import uuid
import json

class MouthPiece():
    def send(self, host, port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect( (host, port))
            sock.sendall(message.encode('ascii'))

    def listenServer(self):
        host = "localhost"
        port = 9002

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        packet = json.loads(self.request.recv(1024))

        if packet["message_type"] == 'sendmessage':
            print(packet['content'])
        if packet["message_type"] == 'invite':
            roomId = pacekt['roomId']


""" 
    Implementation of user's mechanism for chat room
        - createRoom
        - invite
        - leave
        - sendmessage
    all function need a local kademlia peer target
"""

class User(MouthPiece, socketserver.TCPServer):

    def __init__(self, handler):
        socketserver.TCPServer.__init__(self, ("localhost", 9002), handler)
        self.serve_forever()

    """ 
        new a roomId, and record it in kademlia peer's roomInfo.
    """
    def createRoom(self, rpc):
        roomId = uuid.uuid4()
        print("創造新的群組... ", roomId)
        userName = rpc.peer.info
        toUpdateRoomInfo = rpc.peer.roomInfo
        newRoomRecord = {str(roomId) : userName}

        toUpdateRoomInfo.update(newRoomRecord)
        print("新增到群組列表... %s " % toUpdateRoomInfo)

    def invite(self, target, roomId, rpc):
        target.ping(socket = rpc.server.socket,
                    peer_id = rpc.peer.id,
                    peer_info = rpc.peer.info)
        
        message = json.dumps(message)
        self.send(target[0], 9001, message)

    def leave(self, roomId, rpc):
        for target in roomId.items():
            message = json.dump({"user_name" : rpc.peer.info, "message_type" : 'leave', "roomId" : roomId.keys()})
            self.send(target[0], 9001, message)

        del rpc.peer.roomInfo['roomId']
        
    def sendMessage(self, message, target, rpc):
        """target.ping(socket = rpc.server.socket,
                    peer_id = rpc.peer.id,
                    peer_info = rpc.peer.info)
        """
        
        message = json.dumps(message)
        self.send(target[0], 9001, message)

