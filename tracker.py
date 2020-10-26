import socketserver
import threading
import random
import uuid
import json

host = "localhost"
port = 9000

class Handler(socketserver.BaseRequestHandler):
    
    def handle(self):
        data = json.loads(self.request.recv(1024))
        
        if data['message_type'] == 'join':
            accountInfo = {data['user_name'] : data['peer_info']}
            response = self.server.join(accountInfo)
            if response:
                response = bytes(str(response), 'ascii')
            else:
                response = bytes('join completed!\nBut theres no seed in the kademlia network.', 'ascii')

        elif data['message_type'] == 'offline':
            user_name = data['user_name']
            self.server.offline(user_name)
            response = bytes('ok', 'ascii')

        else:
            response = bytes("Hello I'm BootServer, please enter a valid command.", "ascii")

        self.request.sendall(response)

class BootServer(socketserver.TCPServer):
    
    def __init__(self, address, handler):
        socketserver.TCPServer.__init__(self, (host, port), handler)
        self.userList = {}
        print("Boot Server Start!")
        print("目前線上節點: %s\n " % self.userList)
        
    def join(self, accountInfo):
        if self.userList:
            seed = random.choice(list(self.userList.keys() ))
            seed = self.userList[seed]
        else:
            seed = None
        print("更新節點資訊...")
        self.userList.update(accountInfo)
        print("目前線上節點: %s\n" % self.userList)
        return seed

    def offline(self, accountInfo):
        print("收到離線訊息...")
        self.userList.pop(accountInfo)
        print("更新節點資訊...")
        print("目前線上節點: %s\n" % self.userList)

if __name__ == "__main__":
    try:
        server = BootServer( (host, port), Handler )
        server.serve_forever()

    except KeyboardInterrupt:
        threading.Thread(target = server.server_close())
        print("\nServer close.")
