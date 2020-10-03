from kad import DHT
from art import *
from hashing import random_id
import socket
import json

host = "localhost"
port = 9000
nodeInfo = None

class chatroom():
    
    def __init__(self):
        self.tip = None
        self.username = None
        mov = self.intro()
        
        global nodeInfo
        nodeInfo = self.initialize()
        request = json.dumps({"user_name" : self.username, "message_type" : mov, "peer_info" : nodeInfo})
        self._login(request)
         
    def _login(self, request):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect( (host, port) )
                sock.sendall(request.encode("ascii"))
                response = str(sock.recv(1024), "ascii")
                print("Received: {}".format(response) )
        except OSError as e:
            print("registry process failed, please try again")

    def initialize(self):
        nodeId = random_id()
        localPort = 9001
        return (host, localPort, nodeId) 

    def intro(self):
        tfont = "standard"
        tprint("Welcom to P2Pchat, tfont")
        tprint("Please enter your username:", tfont)
        self.username = input()
        
        print("join the kad network? ")
        mov = input()
        return mov

if __name__ == "__main__":
    chat = chatroom()
    local = DHT(host = nodeInfo[0], port = nodeInfo[1], id = nodeInfo[2], info = chat.username)
